"""Escritura incremental del manifiesto JSONL."""

from __future__ import annotations

from pathlib import Path

from ..records import FrameRecord


class JsonlWriter:
    def __init__(self, path: str | Path | None, *, flush_every: int = 30) -> None:
        self.path = Path(path) if path is not None else None
        self._file = None
        self._flush_every = max(1, flush_every)
        self._written = 0
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._file = self.path.open("w", encoding="utf-8")

    def write(self, record: FrameRecord) -> None:
        if self._file is None:
            return
        self._file.write(record.model_dump_json())
        self._file.write("\n")
        self._written += 1
        if self._written % self._flush_every == 0:
            self._file.flush()

    def close(self) -> None:
        if self._file is not None:
            self._file.flush()
            self._file.close()
            self._file = None

    def __enter__(self) -> "JsonlWriter":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()
