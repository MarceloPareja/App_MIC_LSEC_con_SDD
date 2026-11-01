"""Orquestación del pipeline de video."""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .capture import FrameSource
from .config import AppConfig
from .filters import FilterContext, build_filter_chain
from .filters.person_mask import MaskProvider, create_mask_provider
from .geometry import Transform, build_transform
from .io import JsonlWriter, VideoFrameWriter, save_frame_image
from .landmarks import LandmarkSmoother, Landmarks, MediaPipeLandmarker
from .metrics import RunMetrics
from .records import (
    FilterInfo,
    FrameRecord,
    ImageInfo,
    LandmarkRecord,
    SkeletonInfo,
    SourceInfo,
    TransformInfo,
)
from .render import RenderResult, SkeletonConfig, SkeletonRenderer, load_skeleton_config

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineResult:
    summary: dict[str, Any]
    session_id: str
    video_path: Path | None
    jsonl_path: Path | None
    metrics_path: Path | None
    frames_dir: Path | None


def _resolve_path(value: str | None, output_dir: str | None = None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = Path.cwd() / path
    if output_dir:
        path = Path(output_dir).resolve() / path.name
    return path


class VideoPipeline:
    """Captura -> geometría -> landmarks -> filtros -> render -> salidas."""

    def __init__(
        self,
        config: AppConfig,
        *,
        source_path: str | None = None,
        max_frames: int | None = None,
        write_video: bool = True,
        write_jsonl: bool = True,
        save_frames: str | None = None,
        description: str | None = None,
        show: bool | None = None,
        output_dir: str | None = None,
    ) -> None:
        self.config = config
        self.source_path = source_path
        self.max_frames = max_frames
        self.write_video = write_video
        self.write_jsonl = write_jsonl
        self.save_frames = save_frames or config.output.frames
        self.description = (
            description if description is not None else config.output.description
        )
        self.show = config.runtime.show if show is None else show
        self.output_dir = output_dir
        self.session_id = ""
        self._transform: Transform | None = None

    def run(self) -> PipelineResult:
        source = FrameSource(
            self.config.source,
            queue_size=self.config.runtime.queue_size,
            drop_policy=self.config.runtime.drop_policy,
            source_override=self.source_path,
            max_frames=self.max_frames,
        )
        engine: MediaPipeLandmarker | None = None
        mask_provider: MaskProvider | None = None
        filters = []
        video_writer: VideoFrameWriter | None = None
        jsonl_writer: JsonlWriter | None = None
        renderer: SkeletonRenderer | None = None
        skeleton_config: SkeletonConfig | None = None
        video_path: Path | None = None
        jsonl_path: Path | None = None
        metrics_path: Path | None = None
        frames_dir: Path | None = None

        session_start = datetime.now(timezone.utc)
        self.session_id = (
            f"ses_{session_start.strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
        )
        metrics = RunMetrics(
            warmup_frames=self.config.runtime.warmup_frames,
            min_fps=self.config.runtime.min_fps,
        )

        try:
            info = source.start()
            metrics.dropped_frames = source.dropped_frames
            self._transform = build_transform((info.width, info.height), self.config.crop)

            if self.config.skeleton.enabled and self.config.landmarks.enabled:
                skeleton_config = load_skeleton_config(self.config.skeleton.path)
                if (
                    skeleton_config.source == "holistic"
                    and self.config.landmarks.model != "holistic"
                ):
                    raise ValueError(
                        "El esqueleto requiere landmarks.model='holistic' para puntos de "
                        "manos/rostro. Cambia landmarks.model o usa pose_default.json."
                    )
                renderer = SkeletonRenderer(skeleton_config)
            elif self.config.skeleton.enabled:
                logger.warning(
                    "landmarks.enabled=false: no se dibujará esqueleto aunque skeleton.enabled=true."
                )

            if self.config.landmarks.enabled:
                engine = MediaPipeLandmarker(self.config.landmarks)
            smoother = LandmarkSmoother(self.config.landmarks.smoothing)
            mask_provider = create_mask_provider(self.config.mask)
            filters = build_filter_chain(self.config.filters)

            output_size = self.config.crop.output_size
            setup_context = FilterContext(
                frame_index=0,
                timestamp_ms=0.0,
                output_size=output_size,
            )
            for video_filter in filters:
                video_filter.setup(setup_context)

            video_path = _resolve_path(
                self.config.output.video if self.write_video else None, self.output_dir
            )
            jsonl_path = _resolve_path(
                self.config.output.jsonl if self.write_jsonl else None, self.output_dir
            )
            metrics_path = _resolve_path(self.config.output.metrics, self.output_dir)
            if self.save_frames != "none":
                frames_dir = _resolve_path(self.config.output.frame_dir, self.output_dir)

            if video_path is not None:
                output_fps = (
                    self.config.output.fps
                    or (info.effective_fps if info.effective_fps > 0 else 30.0)
                )
                video_writer = VideoFrameWriter(
                    video_path,
                    fps=output_fps,
                    size=output_size,
                    fourcc=self.config.output.fourcc,
                )
            if jsonl_path is not None:
                jsonl_writer = JsonlWriter(jsonl_path)

            last_mask: np.ndarray | None = None
            analysis_size = self.config.landmarks.analysis_size
            filter_context = FilterContext(
                frame_index=0,
                timestamp_ms=0.0,
                output_size=output_size,
            )
            show_enabled = self.show

            while True:
                captured = source.read(timeout=10.0)
                if captured is None:
                    break

                frame_started = time.perf_counter()
                frame = captured.frame
                assert self._transform is not None
                output_frame = self._transform.apply(frame)
                analysis_frame = cv2.resize(
                    output_frame,
                    analysis_size,
                    interpolation=(
                        cv2.INTER_AREA
                        if analysis_size[0] < output_size[0]
                        else cv2.INTER_LINEAR
                    ),
                )

                landmarks: Landmarks = {}
                if engine is not None:
                    landmarks = engine.detect(analysis_frame, captured.timestamp_ms)
                    landmarks = smoother.apply(landmarks)

                if (
                    last_mask is None
                    or captured.index % max(1, self.config.mask.every_n) == 0
                ):
                    assert mask_provider is not None
                    last_mask = mask_provider.get(
                        analysis_frame,
                        landmarks,
                        captured.timestamp_ms,
                        output_size,
                    )
                mask = last_mask

                filter_context.frame_index = captured.index
                filter_context.timestamp_ms = captured.timestamp_ms
                filter_context.mask = mask
                filter_context.landmarks = landmarks

                for video_filter in filters:
                    output_frame = video_filter.apply(output_frame, filter_context)

                render_result = RenderResult()
                if renderer is not None and skeleton_config is not None:
                    render_result = renderer.draw(output_frame, landmarks)

                frame_id = f"frm_{captured.index:06d}"
                image_path: Path | None = None
                should_save = self.save_frames == "all" or (
                    self.save_frames == "keyframes"
                    and captured.index % max(1, self.config.output.every_n) == 0
                )
                if should_save and frames_dir is not None:
                    image_name = f"{frame_id}.{self.config.output.frame_format}"
                    image_path = save_frame_image(
                        output_frame,
                        frames_dir / image_name,
                        frame_format=self.config.output.frame_format,
                        jpeg_quality=self.config.output.jpeg_quality,
                    )
                if video_writer is not None:
                    video_writer.write(output_frame)

                # Se mide computación + escritura de video/imagen (no el JSONL).
                process_ms = (time.perf_counter() - frame_started) * 1000.0
                metrics.add(
                    process_ms=process_ms,
                    timestamp_ms=captured.timestamp_ms,
                    wall_time=time.perf_counter(),
                )
                metrics.dropped_frames = source.dropped_frames
                rolling_fps = metrics.rolling_fps()

                timestamp_iso = (
                    session_start + timedelta(milliseconds=captured.timestamp_ms)
                ).isoformat(timespec="milliseconds").replace("+00:00", "Z")
                record = FrameRecord(
                    session_id=self.session_id,
                    frame_id=frame_id,
                    frame_index=captured.index,
                    timestamp_ms=round(captured.timestamp_ms, 3),
                    timestamp_iso=timestamp_iso,
                    description=self.description,
                    source=SourceInfo(
                        type=info.type,
                        path=info.path if info.type == "file" else None,
                        width=info.width,
                        height=info.height,
                        fps=round(info.fps, 3),
                    ),
                    transform=TransformInfo(**self._transform.to_dict()),
                    image=ImageInfo(
                        path=str(image_path) if image_path is not None else None,
                        width=output_size[0],
                        height=output_size[1],
                    ),
                    landmarks=self._landmark_records(landmarks),
                    skeleton=SkeletonInfo(
                        config=self.config.skeleton.path if skeleton_config else None,
                        points_drawn=render_result.points_drawn,
                        connections_drawn=render_result.connections_drawn,
                    ),
                    filters=[FilterInfo(**video_filter.describe()) for video_filter in filters],
                    metrics={
                        "process_ms": round(process_ms, 3),
                        "fps_rolling": round(rolling_fps, 3),
                    },
                )
                if jsonl_writer is not None:
                    jsonl_writer.write(record)

                if captured.index % 30 == 0:
                    logger.info(
                        "frame=%d ts=%.1fms fps~=%.1f",
                        captured.index,
                        captured.timestamp_ms,
                        rolling_fps,
                    )

                if show_enabled:
                    try:
                        cv2.imshow("vision-pipeline", output_frame)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break
                    except cv2.error as exc:
                        logger.warning("No se puede mostrar video (%s); show desactivado.", exc)
                        show_enabled = False

            summary = metrics.summary()
            summary.update(
                {
                    "session_id": self.session_id,
                    "description": self.description,
                    "source": {
                        "type": info.type,
                        "path": info.path,
                        "width": info.width,
                        "height": info.height,
                        "fps": round(info.fps, 3),
                    },
                    "crop": self._transform.to_dict(),
                    "output_size": list(output_size),
                    "filters": [video_filter.describe() for video_filter in filters],
                    "landmarks_model": (
                        self.config.landmarks.model if self.config.landmarks.enabled else None
                    ),
                    "video": str(video_path) if video_path else None,
                    "jsonl": str(jsonl_path) if jsonl_path else None,
                }
            )
            if metrics_path is not None:
                metrics_path.parent.mkdir(parents=True, exist_ok=True)
                metrics_path.write_text(
                    json.dumps(summary, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            return PipelineResult(
                summary=summary,
                session_id=self.session_id,
                video_path=video_path,
                jsonl_path=jsonl_path,
                metrics_path=metrics_path,
                frames_dir=frames_dir,
            )
        finally:
            source.stop()
            if engine is not None:
                engine.close()
            if mask_provider is not None:
                mask_provider.close()
            for video_filter in filters:
                video_filter.close()
            if video_writer is not None:
                video_writer.close()
            if jsonl_writer is not None:
                jsonl_writer.close()
            if self.show:
                cv2.destroyAllWindows()

    @staticmethod
    def _landmark_records(landmarks: Landmarks) -> dict[str, list[LandmarkRecord]]:
        records: dict[str, list[LandmarkRecord]] = {}
        for group, items in landmarks.items():
            records[group] = [
                LandmarkRecord(
                    id=index,
                    name=item.name,
                    x=round(item.x, 6),
                    y=round(item.y, 6),
                    z=round(item.z, 6),
                    visibility=round(item.visibility, 6),
                )
                for index, item in enumerate(items)
            ]
        return records
