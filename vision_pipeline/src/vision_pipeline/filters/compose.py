"""Composición de un frame filtrado con una máscara de persona."""

from __future__ import annotations

import cv2
import numpy as np


def ensure_mask(
    mask: np.ndarray,
    output_size: tuple[int, int],
) -> np.ndarray:
    """Normaliza la máscara a ``float32 [0,1]`` con el tamaño de salida."""

    normalized = np.asarray(mask, dtype=np.float32)
    if normalized.ndim == 3:
        normalized = normalized[..., 0]
    normalized = np.clip(normalized, 0.0, 1.0)
    height, width = output_size[1], output_size[0]
    if normalized.shape[:2] != (height, width):
        normalized = cv2.resize(normalized, (width, height), interpolation=cv2.INTER_LINEAR)
    return normalized


def feather_mask(mask: np.ndarray, feather: int) -> np.ndarray:
    if feather <= 0:
        return mask
    return cv2.GaussianBlur(mask, (0, 0), sigmaX=float(feather), sigmaY=float(feather))


def compose_masked(
    frame: np.ndarray,
    filtered: np.ndarray,
    mask: np.ndarray,
    *,
    target: str,
) -> np.ndarray:
    """Mezcla ``filtered`` sobre ``frame`` usando la máscara de persona.

    ``target='person'`` aplica el efecto dentro de la persona; ``'background'``
    lo aplica fuera de ella.
    """

    if frame.shape != filtered.shape:
        raise ValueError(f"Formas incompatibles: {frame.shape} vs {filtered.shape}")
    weight = ensure_mask(mask, (frame.shape[1], frame.shape[0]))
    if target == "background":
        weight = 1.0 - weight
    elif target != "person":
        raise ValueError(f"target inválido: {target!r}")

    weight_3c = weight[..., None]
    base = frame.astype(np.float32)
    effect = filtered.astype(np.float32)
    blended = base * (1.0 - weight_3c) + effect * weight_3c
    return np.clip(blended, 0, 255).astype(np.uint8)
