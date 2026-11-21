"""Nombres de landmarks y descarga de modelos oficiales de MediaPipe."""

from __future__ import annotations

import urllib.request
from pathlib import Path

POSE_LANDMARK_NAMES: tuple[str, ...] = (
    "nose",
    "left_eye_inner",
    "left_eye",
    "left_eye_outer",
    "right_eye_inner",
    "right_eye",
    "right_eye_outer",
    "left_ear",
    "right_ear",
    "mouth_left",
    "mouth_right",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_pinky",
    "right_pinky",
    "left_index",
    "right_index",
    "left_thumb",
    "right_thumb",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index",
)

FACE_LANDMARK_COUNT = 478
HAND_LANDMARK_COUNT = 21

FACE_LANDMARK_NAMES: tuple[str, ...] = tuple(
    f"face_{index}" for index in range(FACE_LANDMARK_COUNT)
)
LEFT_HAND_LANDMARK_NAMES: tuple[str, ...] = tuple(
    f"left_hand_{index}" for index in range(HAND_LANDMARK_COUNT)
)
RIGHT_HAND_LANDMARK_NAMES: tuple[str, ...] = tuple(
    f"right_hand_{index}" for index in range(HAND_LANDMARK_COUNT)
)

POSE_NAMES: frozenset[str] = frozenset(POSE_LANDMARK_NAMES)
HAND_NAMES: frozenset[str] = frozenset(LEFT_HAND_LANDMARK_NAMES + RIGHT_HAND_LANDMARK_NAMES)
FACE_NAMES: frozenset[str] = frozenset(FACE_LANDMARK_NAMES)
ALL_LANDMARK_NAMES: frozenset[str] = POSE_NAMES | HAND_NAMES | FACE_NAMES

MODEL_URLS: dict[str, str] = {
    "pose": (
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
        "pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
    ),
    "holistic": (
        "https://storage.googleapis.com/mediapipe-models/holistic_landmarker/"
        "holistic_landmarker/float16/1/holistic_landmarker.task"
    ),
    "selfie_segmenter": (
        "https://storage.googleapis.com/mediapipe-models/image_segmenter/"
        "selfie_segmenter/float16/latest/selfie_segmenter.tflite"
    ),
}


def ensure_model(
    path: str | Path,
    url: str,
    *,
    auto_download: bool = True,
) -> Path:
    """Devuelve la ruta del modelo, descargándolo la primera vez si hace falta."""

    model_path = Path(path)
    if model_path.is_file() and model_path.stat().st_size > 0:
        return model_path

    if not auto_download:
        raise FileNotFoundError(
            f"No se encontró el modelo {model_path} y auto_download está desactivado."
        )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = model_path.with_suffix(model_path.suffix + ".part")
    print(f"[models] Descargando {url} -> {model_path}")
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            data = response.read()
        temporary_path.write_bytes(data)
        temporary_path.replace(model_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink(missing_ok=True)
    return model_path
