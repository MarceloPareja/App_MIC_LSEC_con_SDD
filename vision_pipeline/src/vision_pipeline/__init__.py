"""Pipeline de video con blur gaussiano, MediaPipe y esqueleto configurable."""

from __future__ import annotations

__version__ = "0.1.0"

from .config import AppConfig, load_config
from .pipeline import PipelineResult, VideoPipeline

__all__ = ["AppConfig", "PipelineResult", "VideoPipeline", "__version__", "load_config"]
