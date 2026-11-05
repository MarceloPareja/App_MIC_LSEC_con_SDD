"""Escritura de salidas del pipeline."""

from __future__ import annotations

from .frame_writer import VideoFrameWriter, save_frame_image
from .jsonl_writer import JsonlWriter

__all__ = ["JsonlWriter", "VideoFrameWriter", "save_frame_image"]
