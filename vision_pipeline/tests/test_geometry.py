from __future__ import annotations

import numpy as np
import pytest

from vision_pipeline.config import CropConfig
from vision_pipeline.geometry import (
    build_transform,
    center_crop_rect,
    parse_aspect,
)


def test_parse_aspect() -> None:
    assert parse_aspect("16:9") == pytest.approx(16 / 9)
    assert parse_aspect("1x1") == pytest.approx(1.0)
    assert parse_aspect(None) is None
    with pytest.raises(ValueError):
        parse_aspect("abc")


def test_center_crop_square() -> None:
    assert center_crop_rect(1920, 1080, 1.0) == (420, 0, 1080, 1080)


def test_center_crop_wide_source() -> None:
    x, y, width, height = center_crop_rect(3840, 1080, 1.0)
    assert width == height == 1080
    assert x == (3840 - 1080) // 2
    assert y == 0


def test_transform_letterbox() -> None:
    config = CropConfig(
        mode="rect",
        rect=(0, 0, 1000, 500),
        output_size=(640, 640),
        letterbox=True,
    )
    transform = build_transform((1000, 500), config)
    assert transform.crop == (0, 0, 1000, 500)
    assert transform.resized_size == (640, 320)
    assert transform.pad == (0, 160)

    frame = np.full((500, 1000, 3), 255, dtype=np.uint8)
    output = transform.apply(frame)
    assert output.shape == (640, 640, 3)
    assert int(output[0].sum()) == 0
    assert int(output[159].sum()) == 0
    assert int(output[160].mean()) == 255
    assert int(output[-1].sum()) == 0


def test_transform_center_square_output() -> None:
    config = CropConfig(mode="center", aspect="1:1", output_size=(640, 640))
    transform = build_transform((1920, 1080), config)
    assert transform.crop == (420, 0, 1080, 1080)
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    assert transform.apply(frame).shape == (640, 640, 3)


def test_normalized_to_source_center() -> None:
    config = CropConfig(
        mode="rect",
        rect=(0, 0, 1000, 500),
        output_size=(640, 640),
        letterbox=True,
    )
    transform = build_transform((1000, 500), config)
    x, y = transform.normalized_to_source(0.5, 0.5)
    assert x == pytest.approx(0.5, abs=1e-5)
    assert y == pytest.approx(0.5, abs=1e-5)
