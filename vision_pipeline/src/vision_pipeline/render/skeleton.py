"""Configuración y dibujo del esqueleto a partir de un JSON de puntos."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..landmarks.schema import Landmarks, flatten_landmarks
from ..models import ALL_LANDMARK_NAMES, POSE_NAMES


class PointStyle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    radius: int = 4
    color: tuple[int, int, int] = (0, 255, 0)
    thickness: int = 1


class HighlightStyle(PointStyle):
    glow: bool = False


class LineStyle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thickness: int = 2
    color: tuple[int, int, int] = (255, 255, 255)


class SkeletonStyles(BaseModel):
    model_config = ConfigDict(extra="forbid")

    point: PointStyle = Field(default_factory=PointStyle)
    line: LineStyle = Field(default_factory=LineStyle)
    highlight: HighlightStyle = Field(default_factory=HighlightStyle)


class SkeletonConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = 1
    source: Literal["pose", "holistic"] = "pose"
    points: dict[str, list[str]]
    connections: list[tuple[str, str]] = Field(default_factory=list)
    styles: SkeletonStyles = Field(default_factory=SkeletonStyles)
    min_visibility: float = 0.5

    @model_validator(mode="after")
    def _validate_landmark_names(self) -> "SkeletonConfig":
        if not 0.0 <= self.min_visibility <= 1.0:
            raise ValueError("min_visibility debe estar en [0, 1]")
        allowed = POSE_NAMES if self.source == "pose" else ALL_LANDMARK_NAMES

        configured: set[str] = set()
        for names in self.points.values():
            configured.update(names)
        for start, end in self.connections:
            configured.update((start, end))

        unknown = sorted(configured - allowed)
        if unknown:
            raise ValueError(
                f"Landmarks desconocidos para source={self.source!r}: {unknown}. "
                "Revisa config/skeleton/*.json"
            )
        for start, end in self.connections:
            if start == end:
                raise ValueError(f"Conexión inválida: {start!r} consigo mismo")
        return self

    @property
    def highlight_points(self) -> set[str]:
        return set(self.points.get("highlight", []))

    def all_points(self) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()
        for names in self.points.values():
            for name in names:
                if name not in seen:
                    ordered.append(name)
                    seen.add(name)
        return ordered


def load_skeleton_config(path: str | Path) -> SkeletonConfig:
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"No existe el JSON de esqueleto: {config_path}")
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    return SkeletonConfig.model_validate(payload)


@dataclass(slots=True)
class RenderResult:
    points_drawn: list[str] = field(default_factory=list)
    connections_drawn: list[list[str]] = field(default_factory=list)


class SkeletonRenderer:
    def __init__(self, config: SkeletonConfig) -> None:
        self.config = config

    @staticmethod
    def _bgr(color: tuple[int, int, int]) -> tuple[int, int, int]:
        red, green, blue = color
        return int(blue), int(green), int(red)

    def draw(self, frame: np.ndarray, landmarks: Landmarks) -> RenderResult:
        result = RenderResult()
        if not landmarks:
            return result

        flattened = flatten_landmarks(landmarks)
        height, width = frame.shape[:2]
        scale = max(0.5, min(width, height) / 640.0)
        min_visibility = self.config.min_visibility

        def visible(name: str):
            landmark = flattened.get(name)
            if landmark is None or landmark.visibility < min_visibility:
                return None
            return landmark

        line_style = self.config.styles.line
        for start_name, end_name in self.config.connections:
            start = visible(start_name)
            end = visible(end_name)
            if start is None or end is None:
                continue
            start_point = (int(round(start.x * width)), int(round(start.y * height)))
            end_point = (int(round(end.x * width)), int(round(end.y * height)))
            cv2.line(
                frame,
                start_point,
                end_point,
                self._bgr(line_style.color),
                max(1, int(round(line_style.thickness * scale))),
                lineType=cv2.LINE_AA,
            )
            result.connections_drawn.append([start_name, end_name])

        highlight = self.config.highlight_points
        for name in self.config.all_points():
            landmark = visible(name)
            if landmark is None:
                continue
            center = (int(round(landmark.x * width)), int(round(landmark.y * height)))
            style = (
                self.config.styles.highlight if name in highlight else self.config.styles.point
            )
            radius = max(1, int(round(style.radius * scale)))
            color = self._bgr(style.color)

            if isinstance(style, HighlightStyle) and style.glow:
                overlay = frame.copy()
                cv2.circle(overlay, center, max(2, int(radius * 2.4)), color, -1, cv2.LINE_AA)
                cv2.addWeighted(overlay, 0.35, frame, 0.65, 0.0, dst=frame)

            cv2.circle(
                frame,
                center,
                radius,
                color,
                max(1, int(round(style.thickness * scale))),
                lineType=cv2.LINE_AA,
            )
            result.points_drawn.append(name)

        return result
