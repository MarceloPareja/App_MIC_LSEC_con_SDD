"""Contrato común de los filtros de video."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..config import FilterConfig
from ..landmarks.schema import Landmarks


@dataclass(slots=True)
class FilterContext:
    frame_index: int
    timestamp_ms: float
    output_size: tuple[int, int]
    mask: np.ndarray | None = None
    landmarks: Landmarks = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


class VideoFilter(ABC):
    """Un filtro recibe y devuelve un frame BGR ``uint8``.

    Añadir un filtro nuevo consiste en crear un módulo en este paquete que
    herede de ``VideoFilter``, decorarlo con ``@register_filter`` y añadir su
    entrada en el array ``filters`` de ``app.json``.
    """

    name: str = "base"

    def __init__(self, config: FilterConfig) -> None:
        self.config = config
        self.enabled = config.enabled

    def setup(self, context: FilterContext) -> None:
        """Inicialización opcional (carga de modelos, kernels, etc.)."""

    @abstractmethod
    def apply(self, frame: np.ndarray, context: FilterContext) -> np.ndarray:
        """Aplica el filtro y devuelve el frame resultante."""

    def describe(self) -> dict[str, Any]:
        return {"name": self.name, **self.config.params}

    def close(self) -> None:
        """Libera recursos opcionales."""
