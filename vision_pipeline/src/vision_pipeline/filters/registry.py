"""Registro de filtros por nombre para poder añadirlos desde JSON."""

from __future__ import annotations

from importlib import import_module
from typing import TypeVar

from ..config import FilterConfig
from .base import VideoFilter

_FILTER_REGISTRY: dict[str, type[VideoFilter]] = {}
FilterType = TypeVar("FilterType", bound=type[VideoFilter])


def register_filter(filter_class: FilterType) -> FilterType:
    name = filter_class.name
    if not name or name == "base":
        raise ValueError("Cada filtro debe declarar un atributo 'name' único")
    if name in _FILTER_REGISTRY and _FILTER_REGISTRY[name] is not filter_class:
        raise ValueError(f"Ya existe un filtro registrado con el nombre {name!r}")
    _FILTER_REGISTRY[name] = filter_class
    return filter_class


def available_filters() -> list[str]:
    return sorted(_FILTER_REGISTRY)


def create_filter(config: FilterConfig) -> VideoFilter:
    filter_class = _FILTER_REGISTRY.get(config.name)
    if filter_class is None:
        # Permite filtros definidos por el usuario en filters/<name>.py.
        try:
            import_module(f"{__package__}.{config.name}")
        except ModuleNotFoundError:
            pass
        filter_class = _FILTER_REGISTRY.get(config.name)
    if filter_class is None:
        raise ValueError(
            f"Filtro desconocido {config.name!r}. Disponibles: {', '.join(available_filters())}"
        )
    return filter_class(config)
