from __future__ import annotations

import numpy as np
import pytest

from vision_pipeline.config import FilterConfig
from vision_pipeline.filters.base import FilterContext
from vision_pipeline.filters.gaussian import GaussianFilter


def test_tensorflow_gaussian_backend() -> None:
    pytest.importorskip("tensorflow")
    config = FilterConfig(
        name="gaussian",
        target="person",
        sigma=2.0,
        radius=4,
        backend="tensorflow",
        device="cpu",
    )
    video_filter = GaussianFilter(config)
    context = FilterContext(frame_index=0, timestamp_ms=0.0, output_size=(64, 64))
    video_filter.setup(context)

    rng = np.random.default_rng(3)
    frame = rng.integers(0, 255, size=(64, 64, 3), dtype=np.uint8)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[20:44, 20:44] = 1.0
    context.mask = mask

    blurred = video_filter.apply(frame, context)
    assert blurred.shape == frame.shape
    assert blurred.dtype == np.uint8
    # target=person: el interior de la máscara se difumina.
    assert not np.array_equal(blurred[32, 32], frame[32, 32])
    # target=person: el fondo queda intacto.
    np.testing.assert_array_equal(blurred[0, 0], frame[0, 0])
