"""Lectura de video en un hilo aparte con cola acotada."""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .config import SourceConfig


@dataclass(slots=True)
class CapturedFrame:
    index: int
    timestamp_ms: float
    frame: np.ndarray
    source_index: int


@dataclass(slots=True)
class SourceInfo:
    type: str
    path: str | None
    width: int
    height: int
    fps: float
    effective_fps: float


class FrameSource:
    """Hilo productor de frames.

    En vivo se prioriza la baja latencia (``drop_policy='oldest'``); para
    archivos se usa ``block`` por defecto para no perder ningún frame.
    """

    def __init__(
        self,
        config: SourceConfig,
        *,
        queue_size: int = 4,
        drop_policy: str = "oldest",
        source_override: str | None = None,
        max_frames: int | None = None,
    ) -> None:
        self._config = config
        self._queue_size = max(1, queue_size)
        # Los archivos no deben perder frames; en vivo sí priorizamos latencia.
        self._drop_policy = "block" if config.type == "file" else drop_policy
        self._source_override = source_override
        self._max_frames = max_frames if max_frames is not None else config.max_frames

        self._queue: queue.Queue[CapturedFrame | None] = queue.Queue(maxsize=self._queue_size)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._capture: cv2.VideoCapture | None = None
        self._start_time = 0.0

        self.info = SourceInfo(
            type=config.type,
            path=source_override or config.path,
            width=0,
            height=0,
            fps=0.0,
            effective_fps=0.0,
        )
        self.dropped_frames = 0

    def start(self) -> SourceInfo:
        target: str | int
        if self._source_override:
            target = self._source_override
        elif self._config.type == "camera":
            target = self._config.index
        else:
            assert self._config.path is not None
            target = self._config.path

        if isinstance(target, str) and not Path(target).exists():
            raise FileNotFoundError(f"No existe el video de entrada: {target}")

        capture = cv2.VideoCapture(target)
        if not capture.isOpened():
            capture.release()
            raise RuntimeError(f"No se pudo abrir la fuente de video: {target}")

        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
        if not (1.0 <= fps <= 240.0):
            fps = 30.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        if width <= 0 or height <= 0:
            ok, first = capture.read()
            if not ok or first is None:
                capture.release()
                raise RuntimeError(f"La fuente no entregó ningún frame: {target}")
            height, width = first.shape[:2]
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if self._config.type == "camera" and self._config.target_fps:
            capture.set(cv2.CAP_PROP_FPS, self._config.target_fps)

        skip = 1
        if self._config.type == "file" and self._config.target_fps:
            skip = max(1, int(round(fps / self._config.target_fps)))
        effective_fps = fps / skip

        self._capture = capture
        self.info = SourceInfo(
            type=self._config.type,
            path=self.info.path,
            width=width,
            height=height,
            fps=fps,
            effective_fps=effective_fps,
        )
        self._start_time = time.monotonic()
        self._thread = threading.Thread(
            target=self._reader_loop,
            args=(skip,),
            name="vision-frame-source",
            daemon=True,
        )
        self._thread.start()
        return self.info

    def _reader_loop(self, skip: int) -> None:
        assert self._capture is not None
        source_index = 0
        output_index = 0
        try:
            while not self._stop_event.is_set():
                ok, frame = self._capture.read()
                if not ok or frame is None:
                    break

                if source_index % skip != 0:
                    source_index += 1
                    continue

                if self._max_frames is not None and output_index >= self._max_frames:
                    break

                if self._config.type == "camera":
                    timestamp_ms = (time.monotonic() - self._start_time) * 1000.0
                else:
                    timestamp_ms = source_index / max(self.info.fps, 1e-9) * 1000.0

                item = CapturedFrame(
                    index=output_index,
                    timestamp_ms=timestamp_ms,
                    frame=frame,
                    source_index=source_index,
                )
                self._put(item)
                output_index += 1
                source_index += 1
        finally:
            self._put_sentinel()
            if self._capture is not None:
                self._capture.release()

    def _put_sentinel(self) -> None:
        while True:
            try:
                self._queue.put_nowait(None)
                return
            except queue.Full:
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    pass

    def _put(self, item: CapturedFrame) -> None:
        if self._drop_policy == "oldest":
            try:
                self._queue.put_nowait(item)
            except queue.Full:
                try:
                    self._queue.get_nowait()
                    self.dropped_frames += 1
                except queue.Empty:
                    pass
                try:
                    self._queue.put_nowait(item)
                except queue.Full:
                    self.dropped_frames += 1
        else:
            while not self._stop_event.is_set():
                try:
                    self._queue.put(item, timeout=0.1)
                    return
                except queue.Full:
                    continue

    def read(self, timeout: float = 5.0) -> CapturedFrame | None:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=3.0)
        if self._capture is not None:
            self._capture.release()
            self._capture = None
