"""Benchmark reproducible del pipeline con un clip sintético.

Uso (desde vision_pipeline/):

    python benchmarks/benchmark_pipeline.py --config config/app.json --frames 300

Genera un video de prueba, ejecuta el pipeline sin codificar video y reporta FPS.
No sustituye a probar con un video real: sirve para comparar configuraciones.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vision_pipeline.config import load_config  # noqa: E402
from vision_pipeline.pipeline import VideoPipeline  # noqa: E402


def generate_synthetic_clip(
    path: Path,
    *,
    frames: int = 300,
    width: int = 1280,
    height: int = 720,
    fps: float = 30.0,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"No se pudo crear el clip sintético {path}")

    rng = np.random.default_rng(7)
    background = rng.integers(0, 255, size=(height, width, 3), dtype=np.uint8)
    background = cv2.GaussianBlur(background, (0, 0), sigmaX=7)

    for index in range(frames):
        frame = background.copy()
        phase = index / max(1, frames)
        center_x = int(width * (0.5 + 0.12 * np.sin(2 * np.pi * phase)))
        center_y = int(height * (0.55 + 0.05 * np.cos(2 * np.pi * phase)))
        cv2.ellipse(
            frame,
            (center_x, center_y),
            (int(width * 0.09), int(height * 0.28)),
            0,
            0,
            360,
            (40, 120, 200),
            -1,
            cv2.LINE_AA,
        )
        cv2.circle(
            frame,
            (center_x, center_y - int(height * 0.28)),
            int(height * 0.06),
            (60, 150, 230),
            -1,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            f"BENCH {index:04d}",
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.4,
            (255, 255, 255),
            3,
            cv2.LINE_AA,
        )
        writer.write(frame)
    writer.release()
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark del pipeline")
    parser.add_argument("--config", default="config/app.json")
    parser.add_argument("--frames", type=int, default=300)
    parser.add_argument("--min-fps", type=float, default=15.0)
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "benchmarks" / "out"))
    parser.add_argument("--jsonl", action="store_true", help="Incluir escritura JSONL")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    config = load_config(config_path)
    config = config.model_copy(
        update={"runtime": config.runtime.model_copy(update={"min_fps": args.min_fps})}
    )

    output_dir = Path(args.output_dir)
    clip_path = generate_synthetic_clip(
        output_dir / "synthetic_input.mp4",
        frames=max(args.frames, 30),
    )

    pipeline = VideoPipeline(
        config,
        source_path=str(clip_path),
        max_frames=args.frames,
        write_video=False,
        write_jsonl=args.jsonl,
        save_frames="none",
        output_dir=str(output_dir),
    )
    result = pipeline.run()
    print(json.dumps(result.summary, ensure_ascii=False, indent=2))
    summary = result.summary
    print(
        f"Benchmark: {summary['frames']} frames, "
        f"{summary['mean_fps']:.2f} FPS, "
        f"p95={summary['p95_frame_ms']:.1f} ms, "
        f"objetivo={summary['min_fps']} FPS"
    )
    return 0 if summary["meets_min_fps"] else 1


if __name__ == "__main__":
    sys.exit(main())
