from __future__ import annotations

import numpy as np
import pytest

from vision_pipeline.config import FilterConfig
from vision_pipeline.filters.base import FilterContext
from vision_pipeline.filters.compose import compose_masked, ensure_mask
from vision_pipeline.filters.gaussian import GaussianFilter, gaussian_kernel_1d


def test_gaussian_kernel_normalized_and_symmetric() -> None:
    kernel = gaussian_kernel_1d(2.0, radius=6)
    assert len(kernel) == 13
    assert kernel.sum() == pytest.approx(1.0)
    np.testing.assert_allclose(kernel, kernel[::-1], rtol=1e-6)


def test_ensure_mask_resizes_and_squeezes() -> None:
    mask = np.ones((10, 20, 1), dtype=np.float32)
    normalized = ensure_mask(mask, (40, 20))
    assert normalized.shape == (20, 40)
    assert normalized.min() == pytest.approx(1.0)


def test_compose_person_vs_background() -> None:
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    filtered = np.full((10, 10, 3), 100, dtype=np.uint8)
    mask = np.zeros((10, 10), dtype=np.float32)
    mask[3:7, 3:7] = 1.0

    person = compose_masked(frame, filtered, mask, target="person")
    assert person[5, 5, 0] == 100
    assert person[0, 0, 0] == 0

    background = compose_masked(frame, filtered, mask, target="background")
    assert background[5, 5, 0] == 0
    assert background[0, 0, 0] == 100


def test_gaussian_filter_opencv_backend_uses_mask() -> None:
    config = FilterConfig(
        name="gaussian",
        target="background",
        sigma=3.0,
        radius=3,
        backend="opencv",
    )
    video_filter = GaussianFilter(config)
    context = FilterContext(frame_index=0, timestamp_ms=0.0, output_size=(64, 64))
    video_filter.setup(context)

    frame = np.random.default_rng(0).integers(0, 255, size=(64, 64, 3), dtype=np.uint8)
    frame[20:40, 20:40] = (200, 200, 200)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[20:40, 20:40] = 1.0
    context.mask = mask

    blurred = video_filter.apply(frame, context)
    assert blurred.shape == frame.shape
    # El centro de la persona (máscara=1) no cambia; el borde del fondo sí.
    np.testing.assert_array_equal(blurred[30, 30], frame[30, 30])
    assert not np.array_equal(blurred[0, 0], frame[0, 0])
