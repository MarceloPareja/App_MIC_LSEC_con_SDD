"""Modelos del registro JSON por frame (contrato de salida)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LandmarkRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0


class SourceInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    path: str | None
    width: int
    height: int
    fps: float


class TransformInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    crop: list[int]
    output: list[int]
    scale: float
    pad: list[int]


class ImageInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str | None
    width: int
    height: int


class SkeletonInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config: str | None
    points_drawn: list[str] = Field(default_factory=list)
    connections_drawn: list[list[str]] = Field(default_factory=list)


class FilterInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str


class FrameRecord(BaseModel):
    """Un frame procesado. Se serializa como una línea de ``frames.jsonl``."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    session_id: str
    frame_id: str
    frame_index: int
    timestamp_ms: float
    timestamp_iso: str
    description: str = ""
    source: SourceInfo
    transform: TransformInfo
    image: ImageInfo
    landmarks: dict[str, list[LandmarkRecord]] = Field(default_factory=dict)
    skeleton: SkeletonInfo
    filters: list[FilterInfo] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
