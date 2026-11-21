"""Proveedores de máscara de persona.

La máscara se devuelve siempre a resolución de salida y en ``float32 [0,1]``:
1.0 = persona, 0.0 = fondo.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import cv2
import numpy as np

from ..config import MaskConfig
from ..landmarks.schema import Landmarks, flatten_landmarks
from ..models import MODEL_URLS, ensure_model
from .compose import feather_mask

logger = logging.getLogger(__name__)


class MaskProvider(ABC):
    def __init__(self, config: MaskConfig) -> None:
        self.config = config
        self._previous: np.ndarray | None = None

    def get(
        self,
        frame_bgr: np.ndarray,
        landmarks: Landmarks,
        timestamp_ms: float,
        output_size: tuple[int, int],
    ) -> np.ndarray | None:
        raise NotImplementedError

    def _finalize(self, mask: np.ndarray, output_size: tuple[int, int]) -> np.ndarray:
        width, height = output_size
        normalized = np.asarray(mask, dtype=np.float32)
        if normalized.ndim == 3:
            normalized = normalized[..., 0]
        normalized = np.clip(normalized, 0.0, 1.0)
        if normalized.shape[:2] != (height, width):
            normalized = cv2.resize(
                normalized, (width, height), interpolation=cv2.INTER_LINEAR
            )
        if self.config.feather > 0:
            normalized = feather_mask(normalized, self.config.feather)
        if self._previous is not None and self.config.smoothing > 0:
            alpha = self.config.smoothing
            normalized = alpha * self._previous + (1.0 - alpha) * normalized
        self._previous = normalized
        return np.clip(normalized, 0.0, 1.0)

    def close(self) -> None:
        """Libera recursos opcionales."""


class EllipseMaskProvider(MaskProvider):
    """ROI elíptica central; no necesita modelos y sirve de fallback."""

    def __init__(self, config: MaskConfig) -> None:
        super().__init__(config)
        self._cache: tuple[tuple[int, int], np.ndarray] | None = None

    def _ellipse(self, output_size: tuple[int, int]) -> np.ndarray:
        width, height = output_size
        cx, cy, rx, ry = self.config.ellipse
        mask = np.zeros((height, width), dtype=np.float32)
        center = (int(round(cx * width)), int(round(cy * height)))
        axes = (
            max(1, int(round(rx * width))),
            max(1, int(round(ry * height))),
        )
        cv2.ellipse(mask, center, axes, 0.0, 0.0, 360.0, 1.0, thickness=-1)
        return mask

    def get(
        self,
        frame_bgr: np.ndarray,
        landmarks: Landmarks,
        timestamp_ms: float,
        output_size: tuple[int, int],
    ) -> np.ndarray:
        if self._cache is None or self._cache[0] != output_size:
            self._cache = (output_size, self._finalize(self._ellipse(output_size), output_size))
        return self._cache[1]


class PoseBBoxMaskProvider(MaskProvider):
    """Caja envolvente de los landmarks de pose visibles."""

    def __init__(self, config: MaskConfig) -> None:
        super().__init__(config)
        self._fallback = EllipseMaskProvider(config)

    def get(
        self,
        frame_bgr: np.ndarray,
        landmarks: Landmarks,
        timestamp_ms: float,
        output_size: tuple[int, int],
    ) -> np.ndarray:
        width, height = output_size
        points = [
            (landmark.x, landmark.y)
            for landmark in landmarks.get("pose", [])
            if landmark.visibility >= 0.2
        ]
        if not points:
            return self._fallback.get(frame_bgr, landmarks, timestamp_ms, output_size)

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        expand = self.config.expand
        x0 = max(0.0, min(xs) - expand)
        x1 = min(1.0, max(xs) + expand)
        y0 = max(0.0, min(ys) - expand)
        y1 = min(1.0, max(ys) + expand)

        mask = np.zeros((height, width), dtype=np.float32)
        left = int(round(x0 * width))
        right = int(round(x1 * width))
        top = int(round(y0 * height))
        bottom = int(round(y1 * height))
        cv2.rectangle(mask, (left, top), (right, bottom), 1.0, thickness=-1)
        return self._finalize(mask, output_size)


class SelfieSegmenterMaskProvider(MaskProvider):
    """Segmentación de persona con MediaPipe Tasks ImageSegmenter."""

    def __init__(self, config: MaskConfig) -> None:
        super().__init__(config)
        self._fallback = EllipseMaskProvider(config)
        self._segmenter = None
        self._mp = None
        self._last_timestamp_ms = -1
        try:
            self._initialize()
        except Exception as exc:  # pragma: no cover - depende del entorno
            logger.warning(
                "No se pudo inicializar selfie_segmenter (%s); se usará la elipse central.",
                exc,
            )

    def _initialize(self) -> None:
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision

        model_path = ensure_model(
            Path(self.config.model_path),
            MODEL_URLS["selfie_segmenter"],
            auto_download=self.config.auto_download,
        )
        options = vision.ImageSegmenterOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            output_category_mask=False,
            output_confidence_masks=True,
        )
        self._segmenter = vision.ImageSegmenter.create_from_options(options)
        self._mp = mp

    def get(
        self,
        frame_bgr: np.ndarray,
        landmarks: Landmarks,
        timestamp_ms: float,
        output_size: tuple[int, int],
    ) -> np.ndarray:
        if self._segmenter is None or self._mp is None:
            return self._fallback.get(frame_bgr, landmarks, timestamp_ms, output_size)

        try:
            timestamp = max(int(round(timestamp_ms)), self._last_timestamp_ms + 1)
            self._last_timestamp_ms = timestamp
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            image = self._mp.Image(
                image_format=self._mp.ImageFormat.SRGB,
                data=np.ascontiguousarray(rgb),
            )
            result = self._segmenter.segment_for_video(image, timestamp)
            confidence_masks = result.confidence_masks or []
            if not confidence_masks:
                raise RuntimeError("El segmentador no devolvió máscaras")
            # La última máscara es la de persona en los modelos selfie.
            raw = np.asarray(confidence_masks[-1].numpy_view(), dtype=np.float32)
            return self._finalize(raw, output_size)
        except Exception as exc:  # pragma: no cover - depende del entorno
            logger.warning("Fallo de segmentación (%s); se usará la elipse central.", exc)
            return self._fallback.get(frame_bgr, landmarks, timestamp_ms, output_size)

    def close(self) -> None:
        if self._segmenter is not None:
            self._segmenter.close()
            self._segmenter = None


def create_mask_provider(config: MaskConfig) -> MaskProvider:
    if config.provider == "ellipse":
        return EllipseMaskProvider(config)
    if config.provider == "pose_bbox":
        return PoseBBoxMaskProvider(config)
    if config.provider == "selfie_segmenter":
        return SelfieSegmenterMaskProvider(config)
    raise ValueError(f"Proveedor de máscara desconocido: {config.provider!r}")
