"""CLI: run, benchmark y validate-config."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .config import load_config
from .filters import available_filters, create_filter
from .pipeline import VideoPipeline
from .render import load_skeleton_config

logger = logging.getLogger("vision_pipeline")


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        default="config/app.json",
        help="Ruta al JSON de configuración (por defecto config/app.json)",
    )
    parser.add_argument("--source", default=None, help="Sobrescribe source.path")
    parser.add_argument("--description", default=None, help="Descripción para todos los frames")
    parser.add_argument("--max-frames", type=int, default=None, help="Límite de frames a procesar")
    parser.add_argument("--output-dir", default=None, help="Directorio alternativo para salidas")
    parser.add_argument(
        "--frames",
        choices=["none", "all", "keyframes"],
        default=None,
        help="Sobrescribe output.frames",
    )
    parser.add_argument("--no-video", action="store_true", help="No escribir el video de salida")
    parser.add_argument("--no-jsonl", action="store_true", help="No escribir frames.jsonl")
    parser.add_argument(
        "--show",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Mostrar el video procesado en una ventana",
    )


def _run_pipeline(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    if args.min_fps is not None:
        config = config.model_copy(
            update={"runtime": config.runtime.model_copy(update={"min_fps": args.min_fps})}
        )
    pipeline = VideoPipeline(
        config,
        source_path=args.source,
        max_frames=args.max_frames,
        write_video=not args.no_video,
        write_jsonl=not args.no_jsonl,
        save_frames=args.frames,
        description=args.description,
        show=args.show,
        output_dir=args.output_dir,
    )
    result = pipeline.run()
    printable = dict(result.summary)
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    print(
        "Resumen: "
        f"{printable['frames']} frames, "
        f"{printable['mean_fps']:.2f} FPS medios, "
        f"p95={printable['p95_frame_ms']:.1f} ms, "
        f"mínimo={printable['min_fps']} FPS -> "
        f"{'OK' if printable['meets_min_fps'] else 'POR DEBAJO'}"
    )
    if args.command == "benchmark" and not printable["meets_min_fps"]:
        return 1
    return 0


def _benchmark(args: argparse.Namespace) -> int:
    # El benchmark reutiliza el pipeline real, pero sin codificar video ni guardar frames.
    args.no_video = True
    args.frames = "none"
    args.no_jsonl = True
    if args.max_frames is None:
        args.max_frames = 300
    return _run_pipeline(args)


def _validate(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    for filter_config in config.filters:
        if filter_config.enabled:
            create_filter(filter_config)
    if config.skeleton.enabled:
        skeleton = load_skeleton_config(config.skeleton.path)
        if skeleton.source == "holistic" and config.landmarks.model != "holistic":
            raise ValueError(
                "skeleton.source='holistic' requiere landmarks.model='holistic' "
                f"(actual: {config.landmarks.model!r})"
            )
    print("Configuración válida.")
    print(f"  Filtros disponibles: {', '.join(available_filters())}")
    print(f"  Filtros activos: {[f.name for f in config.filters if f.enabled]}")
    print(f"  Salida: {config.crop.output_size[0]}x{config.crop.output_size[1]}")
    print(
        "  Landmarks: "
        f"{config.landmarks.model if config.landmarks.enabled else 'desactivados'}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vision-pipeline",
        description="Pipeline de video: blur gaussiano, MediaPipe y esqueleto JSON.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Procesa un video o cámara")
    _add_common_arguments(run_parser)
    run_parser.add_argument("--min-fps", type=float, default=None)
    run_parser.set_defaults(handler=_run_pipeline)

    benchmark_parser = subparsers.add_parser(
        "benchmark", help="Mide FPS del pipeline sin codificar video"
    )
    _add_common_arguments(benchmark_parser)
    benchmark_parser.add_argument("--min-fps", type=float, default=15.0)
    benchmark_parser.set_defaults(handler=_benchmark)

    validate_parser = subparsers.add_parser(
        "validate-config", help="Valida el JSON de configuración y el esqueleto"
    )
    validate_parser.add_argument("--config", default="config/app.json")
    validate_parser.set_defaults(handler=_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.handler(args))
    except KeyboardInterrupt:
        logger.warning("Interrumpido por el usuario.")
        return 130
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        logger.error("%s", exc)
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
