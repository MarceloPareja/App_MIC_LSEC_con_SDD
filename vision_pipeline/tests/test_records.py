from __future__ import annotations

import json
from pathlib import Path

from vision_pipeline.records import (
    FilterInfo,
    FrameRecord,
    ImageInfo,
    LandmarkRecord,
    SkeletonInfo,
    SourceInfo,
    TransformInfo,
)


def test_frame_record_roundtrip(tmp_path: Path) -> None:
    record = FrameRecord(
        session_id="ses_test",
        frame_id="frm_000001",
        frame_index=1,
        timestamp_ms=33.333,
        timestamp_iso="2026-10-31T14:03:22.400Z",
        description="",
        source=SourceInfo(
            type="file", path="input.mp4", width=1920, height=1080, fps=30.0
        ),
        transform=TransformInfo(
            crop=[420, 0, 1080, 1080], output=[640, 640], scale=0.5926, pad=[0, 0]
        ),
        image=ImageInfo(path=None, width=640, height=640),
        landmarks={
            "pose": [
                LandmarkRecord(
                    id=0, name="nose", x=0.5, y=0.2, z=-0.1, visibility=0.99
                )
            ]
        },
        skeleton=SkeletonInfo(
            config="config/skeleton/pose_default.json",
            points_drawn=["nose"],
            connections_drawn=[],
        ),
        filters=[FilterInfo(name="gaussian", target="background", sigma=10.0)],
        metrics={"process_ms": 41.2, "fps_rolling": 24.3},
    )

    line = record.model_dump_json()
    payload = json.loads(line)
    assert payload["frame_id"] == "frm_000001"
    assert payload["description"] == ""
    assert payload["landmarks"]["pose"][0]["name"] == "nose"
    assert payload["filters"][0]["target"] == "background"

    path = tmp_path / "frames.jsonl"
    path.write_text(line + "\n", encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8").strip())["session_id"] == "ses_test"
