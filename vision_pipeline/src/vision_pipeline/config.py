"""Configuración tipada del pipeline.

Todos los paths del JSON se resuelven relativos al directorio desde el que se
ejecuta el comando (CWD), igual que hace OpenCV con los archivos de video.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["file", "camera"] = "file"
    path: str | None = None
    index: int = 0
    target_fps: float | None = None
    max_frames: int | None = None

    @model_validator(mode="after")
    def _validate_source(self) -> "SourceConfig":
        if self.type == "file" and not self.path:
            raise ValueError("source.path es obligatorio cuando source.type='file'")
        if self.target_fps is not None and self.target_fps <= 0:
            raise ValueError("source.target_fps debe ser > 0")
        if self.max_frames is not None and self.max_frames <= 0:
            raise ValueError("source.max_frames debe ser > 0")
        return self


class CropConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: Literal["center", "rect"] = "center"
    rect: tuple[int, int, int, int] | None = None
    aspect: str | None = None
    output_size: tuple[int, int] = (640, 640)
    letterbox: bool = True

    @model_validator(mode="after")
    def _validate_crop(self) -> "CropConfig":
        width, height = self.output_size
        if width <= 0 or height <= 0:
            raise ValueError("crop.output_size debe ser [ancho>0, alto>0]")
        if self.mode == "rect":
            if self.rect is None:
                raise ValueError("crop.rect es obligatorio cuando crop.mode='rect'")
            _, _, w, h = self.rect
            if w <= 0 or h <= 0:
                raise ValueError("crop.rect debe tener ancho y alto > 0")
        return self


class MaskConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["ellipse", "pose_bbox", "selfie_segmenter"] = "ellipse"
    model_path: str = "models/selfie_segmenter.tflite"
    auto_download: bool = True
    every_n: int = 2
    smoothing: float = 0.5
    feather: int = 7
    ellipse: tuple[float, float, float, float] = (0.5, 0.5, 0.35, 0.45)
    expand: float = 0.15

    @model_validator(mode="after")
    def _validate_mask(self) -> "MaskConfig":
        if self.every_n < 1:
            raise ValueError("mask.every_n debe ser >= 1")
        if not 0.0 <= self.smoothing < 1.0:
            raise ValueError("mask.smoothing debe estar en [0, 1)")
        if self.feather < 0:
            raise ValueError("mask.feather debe ser >= 0")
        if len(self.ellipse) != 4:
            raise ValueError("mask.ellipse debe ser [cx, cy, rx, ry]")
        if not 0.0 <= self.expand <= 2.0:
            raise ValueError("mask.expand debe estar en [0, 2]")
        return self


class LandmarksConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    model: Literal["pose", "holistic"] = "pose"
    analysis_size: tuple[int, int] = (256, 256)
    smoothing: float = 0.5
    model_path: str = "models/pose_landmarker_lite.task"
    auto_download: bool = True

    @model_validator(mode="after")
    def _validate_landmarks(self) -> "LandmarksConfig":
        width, height = self.analysis_size
        if width <= 0 or height <= 0:
            raise ValueError("landmarks.analysis_size debe ser [ancho>0, alto>0]")
        if not 0.0 <= self.smoothing < 1.0:
            raise ValueError("landmarks.smoothing debe estar en [0, 1)")
        return self


class SkeletonRefConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    path: str = "config/skeleton/pose_default.json"


class FilterConfig(BaseModel):
    """Configuración genérica de un filtro.

    Cada filtro declara sus propios parámetros; los campos desconocidos se
    conservan en ``model_extra`` para que añadir un filtro no obligue a tocar
    el esquema global.
    """

    model_config = ConfigDict(extra="allow", protected_namespaces=())

    name: str
    enabled: bool = True

    @property
    def params(self) -> dict[str, Any]:
        return dict(self.model_extra or {})


class OutputConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    video: str | None = "out/processed.mp4"
    jsonl: str | None = "out/frames.jsonl"
    metrics: str | None = "out/metrics.json"
    frames: Literal["none", "all", "keyframes"] = "keyframes"
    frame_dir: str = "out/frames"
    every_n: int = 30
    frame_format: Literal["jpg", "png"] = "jpg"
    jpeg_quality: int = 90
    fps: float | None = None
    fourcc: str = "mp4v"
    description: str = ""

    @model_validator(mode="after")
    def _validate_output(self) -> "OutputConfig":
        if self.every_n < 1:
            raise ValueError("output.every_n debe ser >= 1")
        if not 0 <= self.jpeg_quality <= 100:
            raise ValueError("output.jpeg_quality debe estar en [0, 100]")
        if self.fps is not None and self.fps <= 0:
            raise ValueError("output.fps debe ser > 0")
        if len(self.fourcc) != 4:
            raise ValueError("output.fourcc debe tener 4 caracteres (p.ej. mp4v, avc1)")
        return self


class RuntimeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queue_size: int = 4
    drop_policy: Literal["oldest", "block"] = "oldest"
    tf_device: str = "auto"
    warmup_frames: int = 30
    min_fps: float = 15.0
    show: bool = False

    @model_validator(mode="after")
    def _validate_runtime(self) -> "RuntimeConfig":
        if self.queue_size < 1:
            raise ValueError("runtime.queue_size debe ser >= 1")
        if self.warmup_frames < 0:
            raise ValueError("runtime.warmup_frames debe ser >= 0")
        if self.min_fps <= 0:
            raise ValueError("runtime.min_fps debe ser > 0")
        return self


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: SourceConfig
    crop: CropConfig = Field(default_factory=CropConfig)
    mask: MaskConfig = Field(default_factory=MaskConfig)
    landmarks: LandmarksConfig = Field(default_factory=LandmarksConfig)
    skeleton: SkeletonRefConfig = Field(default_factory=SkeletonRefConfig)
    filters: list[FilterConfig] = Field(default_factory=list)
    output: OutputConfig = Field(default_factory=OutputConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)


def load_config(path: str | Path) -> AppConfig:
    """Carga y valida ``app.json``."""

    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"No existe el archivo de configuración: {config_path}")
    return AppConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
