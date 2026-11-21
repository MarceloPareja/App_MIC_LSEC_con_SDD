from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from vision_pipeline.config import FilterConfig, SourceConfig, load_config
from vision_pipeline.render import load_skeleton_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_load_app_config() -> None:
    config = load_config(PROJECT_ROOT / "config" / "app.json")
    assert config.crop.output_size == (640, 640)
    assert config.filters[0].name == "gaussian"
    assert config.runtime.min_fps == 15.0


def test_load_holistic_config() -> None:
    config = load_config(PROJECT_ROOT / "config" / "app_holistic.json")
    assert config.landmarks.model == "holistic"
    assert config.skeleton.path.endswith("hands_lsec.json")


def test_filter_extra_params() -> None:
    config = FilterConfig(name="custom", sigma=4, target="person")
    assert config.params == {"sigma": 4, "target": "person"}


def test_source_file_requires_path() -> None:
    with pytest.raises(ValidationError):
        SourceConfig(type="file")


def test_load_skeleton_configs() -> None:
    pose = load_skeleton_config(PROJECT_ROOT / "config" / "skeleton" / "pose_default.json")
    assert "nose" in pose.all_points()
    hands = load_skeleton_config(PROJECT_ROOT / "config" / "skeleton" / "hands_lsec.json")
    assert "left_hand_20" in hands.all_points()


def test_skeleton_rejects_unknown_names(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(
        '{"version": 1, "source": "pose", "points": {"base": ["not_a_landmark"]}}',
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_skeleton_config(path)
