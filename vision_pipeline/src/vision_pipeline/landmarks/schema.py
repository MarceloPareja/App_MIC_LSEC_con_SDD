"""Estructuras internas de landmarks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Landmark:
    name: str
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0


Landmarks = dict[str, list[Landmark]]


def flatten_landmarks(groups: Landmarks) -> dict[str, Landmark]:
    flattened: dict[str, Landmark] = {}
    for landmarks in groups.values():
        for landmark in landmarks:
            flattened[landmark.name] = landmark
    return flattened
