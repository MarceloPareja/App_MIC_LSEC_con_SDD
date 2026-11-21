"""Utilidades de geometría: recorte central, letterbox y mapeo de coordenadas."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import cv2
import numpy as np

from .config import CropConfig


def parse_aspect(aspect: str | None) -> float | None:
    """Convierte ``"16:9"`` en ``16 / 9``. Devuelve ``None`` si no se define."""

    if aspect is None:
        return None
    text = aspect.strip().replace("x", ":").replace("X", ":")
    try:
        width, height = text.split(":", maxsplit=1)
        ratio = float(Fraction(width.strip())) / float(Fraction(height.strip()))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"Aspecto inválido: {aspect!r}. Usa el formato '16:9'.") from exc
    if ratio <= 0:
        raise ValueError(f"Aspecto inválido: {aspect!r}")
    return ratio


def center_crop_rect(
    source_width: int,
    source_height: int,
    target_aspect: float,
) -> tuple[int, int, int, int]:
    """Rectángulo central con el aspecto pedido, lo más grande posible."""

    if source_width <= 0 or source_height <= 0:
        raise ValueError("Las dimensiones de origen deben ser positivas")
    source_aspect = source_width / source_height
    if source_aspect > target_aspect:
        height = source_height
        width = int(round(height * target_aspect))
    else:
        width = source_width
        height = int(round(width / target_aspect))
    width = max(1, min(width, source_width))
    height = max(1, min(height, source_height))
    x = (source_width - width) // 2
    y = (source_height - height) // 2
    return x, y, width, height


def _clamp_rect(
    rect: tuple[int, int, int, int],
    source_width: int,
    source_height: int,
) -> tuple[int, int, int, int]:
    x, y, width, height = rect
    x = max(0, min(x, source_width - 1))
    y = max(0, min(y, source_height - 1))
    width = max(1, min(width, source_width - x))
    height = max(1, min(height, source_height - y))
    return x, y, width, height


@dataclass(frozen=True, slots=True)
class Transform:
    """Transformación frame original -> frame de salida (letterbox)."""

    crop: tuple[int, int, int, int]
    output_size: tuple[int, int]
    resized_size: tuple[int, int]
    scale: float
    pad: tuple[int, int]
    source_size: tuple[int, int] = (1, 1)

    def apply(self, frame: np.ndarray) -> np.ndarray:
        x, y, width, height = self.crop
        cropped = frame[y : y + height, x : x + width]
        if cropped.size == 0:
            raise ValueError(f"Recorte vacío: {self.crop} sobre frame {frame.shape}")

        interpolation = (
            cv2.INTER_AREA
            if self.resized_size[0] < width or self.resized_size[1] < height
            else cv2.INTER_LINEAR
        )
        resized = cv2.resize(cropped, self.resized_size, interpolation=interpolation)

        out_width, out_height = self.output_size
        if self.resized_size == self.output_size:
            return np.ascontiguousarray(resized)

        canvas = np.zeros((out_height, out_width, frame.shape[2]), dtype=frame.dtype)
        pad_x, pad_y = self.pad
        canvas[
            pad_y : pad_y + self.resized_size[1],
            pad_x : pad_x + self.resized_size[0],
        ] = resized
        return canvas

    def to_dict(self) -> dict[str, object]:
        return {
            "crop": list(self.crop),
            "output": list(self.output_size),
            "scale": round(self.scale, 6),
            "pad": list(self.pad),
        }

    def normalized_to_source(self, x: float, y: float) -> tuple[float, float]:
        """Convierte coordenadas normalizadas del frame de salida al original."""

        out_width, out_height = self.output_size
        resized_width, resized_height = self.resized_size
        pad_x, pad_y = self.pad

        pixel_x = x * out_width - pad_x
        pixel_y = y * out_height - pad_y
        crop_x, crop_y, crop_width, crop_height = self.crop
        source_width, source_height = self.source_size
        scale_x = resized_width / max(crop_width, 1)
        scale_y = resized_height / max(crop_height, 1)
        return (
            (crop_x + pixel_x / max(scale_x, 1e-9)) / source_width,
            (crop_y + pixel_y / max(scale_y, 1e-9)) / source_height,
        )


def build_transform(
    source_size: tuple[int, int],
    crop_config: CropConfig,
) -> Transform:
    """Calcula el recorte y el escalado/letterbox hacia la resolución de salida."""

    source_width, source_height = source_size
    output_width, output_height = crop_config.output_size

    if crop_config.mode == "rect":
        assert crop_config.rect is not None
        crop = _clamp_rect(crop_config.rect, source_width, source_height)
    else:
        target_aspect = parse_aspect(crop_config.aspect) or (output_width / output_height)
        crop = center_crop_rect(source_width, source_height, target_aspect)

    _, _, crop_width, crop_height = crop
    if crop_config.letterbox:
        scale = min(output_width / crop_width, output_height / crop_height)
        resized_width = max(1, int(round(crop_width * scale)))
        resized_height = max(1, int(round(crop_height * scale)))
        pad_x = (output_width - resized_width) // 2
        pad_y = (output_height - resized_height) // 2
    else:
        resized_width, resized_height = output_width, output_height
        scale = output_width / crop_width
        pad_x = pad_y = 0

    transform = Transform(
        crop=crop,
        output_size=(output_width, output_height),
        resized_size=(resized_width, resized_height),
        scale=scale,
        pad=(pad_x, pad_y),
        source_size=(source_width, source_height),
    )
    return transform
