"""Suavizado temporal de landmarks (EMA configurable)."""

from __future__ import annotations

from .schema import Landmark, Landmarks


class LandmarkSmoother:
    """EMA por landmark. ``alpha=0`` desactiva el suavizado.

    Un valor alto de ``smoothing`` prioriza el estado anterior (más estable,
    más latencia); un valor bajo prioriza la detección actual.
    """

    def __init__(self, alpha: float = 0.5) -> None:
        if not 0.0 <= alpha < 1.0:
            raise ValueError("smoothing debe estar en [0, 1)")
        self.alpha = alpha
        self._previous: dict[str, tuple[float, float, float, float]] = {}

    def apply(self, groups: Landmarks) -> Landmarks:
        if self.alpha <= 0:
            return groups

        smoothed: Landmarks = {}
        for group, landmarks in groups.items():
            smoothed[group] = [self._smooth(landmark) for landmark in landmarks]
        return smoothed

    def _smooth(self, landmark: Landmark) -> Landmark:
        previous = self._previous.get(landmark.name)
        if previous is None:
            result = Landmark(
                name=landmark.name,
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility,
            )
        else:
            alpha = self.alpha
            result = Landmark(
                name=landmark.name,
                x=alpha * previous[0] + (1.0 - alpha) * landmark.x,
                y=alpha * previous[1] + (1.0 - alpha) * landmark.y,
                z=alpha * previous[2] + (1.0 - alpha) * landmark.z,
                visibility=alpha * previous[3] + (1.0 - alpha) * landmark.visibility,
            )
        self._previous[landmark.name] = (
            result.x,
            result.y,
            result.z,
            result.visibility,
        )
        return result
