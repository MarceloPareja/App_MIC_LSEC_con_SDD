"""Escritura de video e imágenes por frame."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


class VideoFrameWriter:
    def __init__(
        self,
        path: str | Path,
        *,
        fps: float,
        size: tuple[int, int],
        fourcc: str = "mp4v",
    ) -> None:
        self.path = Path(path)
        self.size = size
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._writer = self._open(fourcc, fps, size)

    def _open(self, fourcc: str, fps: float, size: tuple[int, int]) -> cv2.VideoWriter:
        candidates = [fourcc]
        if fourcc.lower() != "mp4v":
            candidates.append("mp4v")
        for code in candidates:
            writer = cv2.VideoWriter(
                str(self.path),
                cv2.VideoWriter_fourcc(*code),
                float(fps),
                size,
            )
            if writer.isOpened():
                return writer
            writer.release()
        raise RuntimeError(
            f"No se pudo abrir el writer de video {self.path} (fourcc={candidates}). "
            "Prueba con output.video=null o cambia output.fourcc."
        )

    def write(self, frame: np.ndarray) -> None:
        height, width = frame.shape[:2]
        if (width, height) != self.size:
            raise ValueError(
                f"Frame de {width}x{height} no coincide con la salida {self.size}"
            )
        self._writer.write(frame)

    def close(self) -> None:
        self._writer.release()

    def __enter__(self) -> "VideoFrameWriter":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()


def save_frame_image(
    frame: np.ndarray,
    path: str | Path,
    *,
    frame_format: str = "jpg",
    jpeg_quality: int = 90,
) -> Path:
    image_path = Path(path)
    image_path.parent.mkdir(parents=True, exist_ok=True)
    params: list[int] = []
    if frame_format.lower() in {"jpg", "jpeg"}:
        params = [cv2.IMWRITE_JPEG_QUALITY, int(jpeg_quality)]
    elif frame_format.lower() == "png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, 3]
    if not cv2.imwrite(str(image_path), frame, params):
        raise RuntimeError(f"No se pudo guardar la imagen {image_path}")
    return image_path
