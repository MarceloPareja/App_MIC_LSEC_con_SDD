from __future__ import annotations

import cv2
import numpy as np
import pytest

from vision_pipeline.landmarks.schema import Landmark
from vision_pipeline.render.skeleton import SkeletonConfig, SkeletonRenderer


def _config() -> SkeletonConfig:
    return SkeletonConfig.model_validate(
        {
            "version": 1,
            "source": "pose",
            "points": {
                "base": ["left_shoulder", "right_shoulder"],
                "highlight": ["nose"],
            },
            "connections": [["left_shoulder", "right_shoulder"]],
            "styles": {
                "point": {"radius": 4, "color": [0, 255, 0]},
                "line": {"thickness": 2, "color": [255, 255, 255]},
                "highlight": {"radius": 7, "color": [0, 200, 255], "glow": True},
            },
            "min_visibility": 0.5,
        }
    )


def test_draws_only_configured_points() -> None:
    frame = np.zeros((640, 640, 3), dtype=np.uint8)
    landmarks = {
        "pose": [
            Landmark("nose", 0.5, 0.3, visibility=0.9),
            Landmark("left_shoulder", 0.35, 0.5, visibility=0.9),
            Landmark("right_shoulder", 0.65, 0.5, visibility=0.9),
            Landmark("left_elbow", 0.3, 0.7, visibility=0.9),
        ]
    }
    result = SkeletonRenderer(_config()).draw(frame, landmarks)

    assert result.points_drawn == ["left_shoulder", "right_shoulder", "nose"]
    assert result.connections_drawn == [["left_shoulder", "right_shoulder"]]
    assert frame[192, 320].any()  # nose dibujado (y=0.3*640=192, x=320)
    # La línea de hombros se dibuja en y=320.
    assert frame[320, 320].any()


def test_low_visibility_is_skipped() -> None:
    frame = np.zeros((640, 640, 3), dtype=np.uint8)
    landmarks = {"pose": [Landmark("nose", 0.5, 0.3, visibility=0.1)]}
    result = SkeletonRenderer(_config()).draw(frame, landmarks)
    assert result.points_drawn == []
    assert not frame.any()


def test_unknown_landmark_rejected() -> None:
    with pytest.raises(ValueError):
        SkeletonConfig.model_validate(
            {
                "version": 1,
                "source": "pose",
                "points": {"base": ["invented_point"]},
            }
        )
