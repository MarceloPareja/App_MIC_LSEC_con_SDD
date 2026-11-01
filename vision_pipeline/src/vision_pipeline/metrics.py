"""Métricas de rendimiento del pipeline."""

from __future__ import annotations

import math
from collections import deque

import numpy as np


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    return float(np.percentile(np.asarray(values, dtype=np.float64), percentile))


class RunMetrics:
    """Acumula latencias y calcula FPS efectivos (ignorando el warm-up)."""

    def __init__(self, *, warmup_frames: int = 0, min_fps: float = 15.0) -> None:
        self._warmup_frames = max(0, warmup_frames)
        self._min_fps = min_fps
        self._all_process_ms: deque[float] = deque(maxlen=10000)
        self._measured_process_ms: list[float] = []
        self.total_frames = 0
        self.dropped_frames = 0
        self._started_at: float | None = None
        self._finished_at: float | None = None
        self._started_ts_ms: float | None = None
        self._finished_ts_ms: float | None = None

    def start(self, timestamp_ms: float, wall_time: float) -> None:
        if self._started_at is None:
            self._started_at = wall_time
        if self._started_ts_ms is None:
            self._started_ts_ms = timestamp_ms

    def add(self, *, process_ms: float, timestamp_ms: float, wall_time: float) -> None:
        self.start(timestamp_ms, wall_time)
        self.total_frames += 1
        self._finished_at = wall_time
        self._finished_ts_ms = timestamp_ms
        self._all_process_ms.append(process_ms)
        # El warm-up (carga de modelos, compilación de tf.function) no cuenta.
        if self.total_frames > self._warmup_frames:
            self._measured_process_ms.append(process_ms)

    def summary(self) -> dict[str, object]:
        frames = self.total_frames
        elapsed_wall = 0.0
        if self._started_at is not None and self._finished_at is not None:
            elapsed_wall = max(0.0, self._finished_at - self._started_at)

        elapsed_video = 0.0
        if self._started_ts_ms is not None and self._finished_ts_ms is not None:
            elapsed_video = max(0.0, (self._finished_ts_ms - self._started_ts_ms) / 1000.0)

        process_ms = list(self._measured_process_ms)
        total_measured_ms = sum(process_ms)
        mean_fps = (
            1000.0 * len(process_ms) / total_measured_ms if total_measured_ms > 0 else 0.0
        )
        wall_fps = frames / elapsed_wall if elapsed_wall > 0 else 0.0
        source_fps = frames / elapsed_video if elapsed_video > 0 else 0.0

        return {
            "frames": frames,
            "measured_frames": len(process_ms),
            "dropped_frames": self.dropped_frames,
            "elapsed_wall_s": round(elapsed_wall, 4),
            "elapsed_video_s": round(elapsed_video, 4),
            "mean_fps": round(mean_fps, 3),
            "wall_fps": round(wall_fps, 3),
            "source_fps": round(source_fps, 3),
            "p50_frame_ms": round(_percentile(process_ms, 50), 3),
            "p95_frame_ms": round(_percentile(process_ms, 95), 3),
            "max_frame_ms": round(max(process_ms) if process_ms else 0.0, 3),
            "min_fps": self._min_fps,
            "meets_min_fps": bool(mean_fps >= self._min_fps) if process_ms else False,
        }

    def rolling_fps(self, window: int = 30) -> float:
        if len(self._all_process_ms) < 2:
            return 0.0
        recent = list(self._all_process_ms)[-window:]
        mean_ms = sum(recent) / len(recent)
        return 1000.0 / mean_ms if mean_ms > 0 else 0.0

    @staticmethod
    def safe_fps(process_ms: float) -> float:
        return 1000.0 / process_ms if process_ms > 0 and not math.isnan(process_ms) else 0.0
