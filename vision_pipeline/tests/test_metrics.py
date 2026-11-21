from __future__ import annotations

from vision_pipeline.metrics import RunMetrics


def test_metrics_summary() -> None:
    metrics = RunMetrics(warmup_frames=0, min_fps=15.0)
    for index in range(10):
        metrics.add(
            process_ms=40.0,
            timestamp_ms=index * 33.0,
            wall_time=index * 0.04,
        )
    summary = metrics.summary()
    assert summary["frames"] == 10
    assert summary["mean_fps"] == 25.0
    assert summary["p50_frame_ms"] == 40.0
    assert summary["meets_min_fps"] is True


def test_warmup_frames_are_excluded() -> None:
    metrics = RunMetrics(warmup_frames=2, min_fps=15.0)
    for index in range(5):
        metrics.add(
            process_ms=1000.0 if index < 2 else 10.0,
            timestamp_ms=index * 33.0,
            wall_time=index * 0.01,
        )
    summary = metrics.summary()
    assert summary["frames"] == 5
    assert summary["measured_frames"] == 3
    assert summary["p95_frame_ms"] == 10.0
