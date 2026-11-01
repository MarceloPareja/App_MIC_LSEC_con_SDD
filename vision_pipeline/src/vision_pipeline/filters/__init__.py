"""Filtros disponibles y fábrica de la cadena."""

from __future__ import annotations

from ..config import FilterConfig
from .base import FilterContext, VideoFilter
from .registry import available_filters, create_filter, register_filter

# Importar los filtros incluidos registra automáticamente sus clases.
from . import gaussian as _gaussian  # noqa: E402,F401


def build_filter_chain(configs: list[FilterConfig]) -> list[VideoFilter]:
    chain: list[VideoFilter] = []
    for config in configs:
        if not config.enabled:
            continue
        chain.append(create_filter(config))
    return chain


__all__ = [
    "FilterContext",
    "VideoFilter",
    "available_filters",
    "build_filter_chain",
    "create_filter",
    "register_filter",
]
