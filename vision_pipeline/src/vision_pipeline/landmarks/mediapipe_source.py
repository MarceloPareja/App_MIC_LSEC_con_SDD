"""Conector con MediaPipe Tasks para obtener landmarks en modo VIDEO."""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

from ..config import LandmarksConfig
from ..models import (
    FACE_LANDMARK_NAMES,
    LEFT_HAND_LANDMARK_NAMES,
    MODEL_URLS,
    POSE_LANDMARK_NAMES,
    RIGHT_HAND_LANDMARK_NAMES,
    ensure_model,
)
from .schema import Landmark, Landmarks

logger = logging.getLogger(__name__)


class MediaPipeLandmarker:
    """Landmarker síncrono por frame.

    Se usa ``RunningMode.VIDEO`` con ``detect_for_video`` para garantizar que
    cada resultado corresponde exactamente al frame que se está procesando.
    """

    def __init__(self, config: LandmarksConfig) -> None:
        self.config = config
        self._mp = None
        self._landmarker = None
        self._mode = config.model
        self._last_timestamp_ms = -1

        model_path = Path(config.model_path)
        if self._mode == "holistic" and model_path.name == "pose_landmarker_lite.task":
            model_path = Path("models/holistic_landmarker.task")
        self._model_path = ensure_model(
            model_path,
            MODEL_URLS[self._mode],
            auto_download=config.auto_download,
        )
        self._initialize()

    def _initialize(self) -> None:
        try:
            import mediapipe as mp
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision
        except ImportError as exc:  # pragma: no cover - depende del entorno
            raise RuntimeError(
                "MediaPipe no está instalado. Instala 'mediapipe' o desactiva "
                "landmarks.enabled en la configuración."
            ) from exc

        base_options = mp_python.BaseOptions(model_asset_path=str(self._model_path))
        if self._mode == "pose":
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                num_poses=1,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5,
                output_segmentation_masks=False,
            )
            self._landmarker = vision.PoseLandmarker.create_from_options(options)
        else:
            options = vision.HolisticLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                min_face_detection_confidence=0.5,
                min_face_landmarks_confidence=0.5,
                min_pose_detection_confidence=0.5,
                min_pose_landmarks_confidence=0.5,
                min_hand_landmarks_confidence=0.5,
                output_segmentation_mask=False,
            )
            self._landmarker = vision.HolisticLandmarker.create_from_options(options)
        self._mp = mp

    def detect(self, frame_bgr: np.ndarray, timestamp_ms: float) -> Landmarks:
        if self._mp is None or self._landmarker is None:
            return {}

        timestamp = max(int(round(timestamp_ms)), self._last_timestamp_ms + 1)
        self._last_timestamp_ms = timestamp
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = self._mp.Image(
            image_format=self._mp.ImageFormat.SRGB,
            data=np.ascontiguousarray(rgb),
        )

        if self._mode == "pose":
            result = self._landmarker.detect_for_video(image, timestamp)
            poses = result.pose_landmarks or []
            return {
                "pose": self._convert(poses[0], POSE_LANDMARK_NAMES, "pose")
                if poses
                else []
            }

        result = self._landmarker.detect_for_video(image, timestamp)
        return {
            "pose": self._convert(result.pose_landmarks, POSE_LANDMARK_NAMES, "pose"),
            "face": self._convert(result.face_landmarks, FACE_LANDMARK_NAMES, "face"),
            "left_hand": self._convert(
                result.left_hand_landmarks, LEFT_HAND_LANDMARK_NAMES, "left_hand"
            ),
            "right_hand": self._convert(
                result.right_hand_landmarks, RIGHT_HAND_LANDMARK_NAMES, "right_hand"
            ),
        }

    @staticmethod
    def _convert(normalized, names: tuple[str, ...], prefix: str) -> list[Landmark]:
        landmarks: list[Landmark] = []
        for index, item in enumerate(normalized or []):
            name = names[index] if index < len(names) else f"{prefix}_{index}"
            visibility = getattr(item, "visibility", None)
            landmarks.append(
                Landmark(
                    name=name,
                    x=float(item.x),
                    y=float(item.y),
                    z=float(getattr(item, "z", 0.0)),
                    visibility=float(visibility) if visibility is not None else 1.0,
                )
            )
        return landmarks

    def close(self) -> None:
        if self._landmarker is not None:
            self._landmarker.close()
            self._landmarker = None
