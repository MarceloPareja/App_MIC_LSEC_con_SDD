"""Filtro gaussiano separable implementado en TensorFlow.

La convolución se hace en dos pasadas (horizontal y vertical) para reducir el
coste de O(k²) a O(2k) por píxel. La máscara de persona permite aplicar el
desenfoque solo a la persona (privacidad) o solo al fondo (resaltado).
"""

from __future__ import annotations

import logging

import cv2
import numpy as np

from ..config import FilterConfig
from .base import FilterContext, VideoFilter
from .compose import ensure_mask, compose_masked
from .registry import register_filter

logger = logging.getLogger(__name__)


def gaussian_kernel_1d(sigma: float, radius: int | None = None) -> np.ndarray:
    """Kernel gaussiano 1D normalizado."""

    if sigma <= 0:
        raise ValueError("sigma debe ser > 0")
    if radius is None:
        radius = int(np.ceil(3.0 * sigma))
    radius = max(1, int(radius))
    positions = np.arange(-radius, radius + 1, dtype=np.float32)
    kernel = np.exp(-(positions**2) / (2.0 * sigma**2))
    return kernel / kernel.sum()


@register_filter
class GaussianFilter(VideoFilter):
    name = "gaussian"

    def __init__(self, config: FilterConfig) -> None:
        super().__init__(config)
        params = config.params
        self.target = str(params.get("target", "background"))
        if self.target not in {"person", "background"}:
            raise ValueError("gaussian.target debe ser 'person' o 'background'")
        self.sigma = float(params.get("sigma", 10.0))
        radius = params.get("radius")
        self.radius = int(radius) if radius is not None else int(np.ceil(3.0 * self.sigma))
        self.radius = max(1, self.radius)
        self.backend = str(params.get("backend", "tensorflow")).lower()
        if self.backend not in {"tensorflow", "opencv", "auto"}:
            raise ValueError("gaussian.backend debe ser 'tensorflow', 'opencv' o 'auto'")
        self.device = str(params.get("device", "auto"))
        if self.sigma <= 0:
            raise ValueError("gaussian.sigma debe ser > 0")

        self._kernel = gaussian_kernel_1d(self.sigma, self.radius)
        self._tf = None
        self._blur_fn = None
        self._effective_backend = self.backend
        self._warned_without_mask = False

    def setup(self, context: FilterContext) -> None:
        if self.backend == "opencv":
            self._effective_backend = "opencv"
            return
        try:
            import tensorflow as tf
        except ImportError as exc:
            if self.backend == "auto":
                logger.warning("TensorFlow no está instalado; se usará OpenCV para el blur.")
                self._effective_backend = "opencv"
                return
            raise RuntimeError(
                "El filtro gaussiano requiere TensorFlow. Instala 'tensorflow' o usa "
                "backend='opencv' en la configuración."
            ) from exc

        tf.get_logger().setLevel("ERROR")
        self._tf = tf
        kernel = tf.constant(self._kernel, dtype=tf.float32)
        radius = self.radius

        def blur(image):
            horizontal = tf.reshape(kernel, [1, -1, 1, 1])
            horizontal = tf.tile(horizontal, [1, 1, 3, 1])
            padded = tf.pad(image, [[0, 0], [0, 0], [radius, radius], [0, 0]], mode="REFLECT")
            image = tf.nn.depthwise_conv2d(
                padded, horizontal, strides=[1, 1, 1, 1], padding="VALID"
            )

            vertical = tf.reshape(kernel, [-1, 1, 1, 1])
            vertical = tf.tile(vertical, [1, 1, 3, 1])
            padded = tf.pad(image, [[0, 0], [radius, radius], [0, 0], [0, 0]], mode="REFLECT")
            return tf.nn.depthwise_conv2d(
                padded, vertical, strides=[1, 1, 1, 1], padding="VALID"
            )

        self._blur_fn = tf.function(
            blur,
            input_signature=[
                tf.TensorSpec(shape=[None, None, None, 3], dtype=tf.float32)
            ],
        )
        self._effective_backend = "tensorflow"

    def _tensorflow_blur(self, frame: np.ndarray) -> np.ndarray:
        assert self._tf is not None and self._blur_fn is not None
        tf = self._tf
        device = self.device
        if device == "auto":
            device = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"
        with tf.device(device):
            tensor = tf.expand_dims(
                tf.convert_to_tensor(frame, dtype=tf.float32), axis=0
            )
            blurred = self._blur_fn(tensor)
            blurred = tf.squeeze(blurred, axis=0)
            blurred = tf.clip_by_value(blurred, 0.0, 255.0)
            return blurred.numpy().astype(np.uint8)

    def _opencv_blur(self, frame: np.ndarray) -> np.ndarray:
        kernel_size = self.radius * 2 + 1
        return cv2.GaussianBlur(
            frame,
            (kernel_size, kernel_size),
            sigmaX=self.sigma,
            sigmaY=self.sigma,
            borderType=cv2.BORDER_REFLECT,
        )

    def apply(self, frame: np.ndarray, context: FilterContext) -> np.ndarray:
        if context.mask is None:
            if not self._warned_without_mask:
                logger.warning(
                    "GaussianFilter sin máscara: no se aplica blur para evitar difuminar "
                    "el frame completo."
                )
                self._warned_without_mask = True
            return frame

        mask = ensure_mask(context.mask, (frame.shape[1], frame.shape[0]))
        if self._effective_backend == "tensorflow" and self._blur_fn is not None:
            blurred = self._tensorflow_blur(frame)
        else:
            blurred = self._opencv_blur(frame)
        return compose_masked(frame, blurred, mask, target=self.target)

    def describe(self) -> dict[str, object]:
        return {
            "name": self.name,
            "target": self.target,
            "sigma": self.sigma,
            "radius": self.radius,
            "backend": self._effective_backend,
        }
