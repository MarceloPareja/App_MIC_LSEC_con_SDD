# Vision Pipeline — blur gaussiano + MediaPipe + esqueleto JSON

Pipeline en Python para procesar video o cámara:

1. Recorta una zona central (o un rectángulo configurable) a una resolución fija.
2. Aplica un **filtro gaussiano separable en TensorFlow** sobre la persona o el fondo.
3. Detecta landmarks con **MediaPipe Tasks** (pose u holistic: pose + manos + rostro).
4. Dibuja solo los puntos y conexiones definidos en un **JSON de esqueleto**.
5. Genera un **video procesado**, un manifiesto **JSONL por frame** y keyframes de imagen.

Por defecto apunta a **≥15 FPS** (se recomienda ≥20 para tener margen).

## Requisitos

- **Python 3.10–3.13** (recomendado 3.11/3.12).
- GPU opcional. El pipeline incluye ruta CPU.
- En Windows se recomienda ejecutar desde PowerShell con el entorno virtual activado.

## Instalación

```powershell
cd vision_pipeline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Los modelos de MediaPipe se descargan automáticamente la primera vez:

- `models/pose_landmarker_lite.task`
- `models/holistic_landmarker.task` (solo si usas `config/app_holistic.json`)
- `models/selfie_segmenter.tflite` (máscara de persona)

Si no hay red, coloca los archivos manualmente en `models/` o activa
`auto_download: false` y usa `mask.provider: "ellipse"`.

## Uso rápido

Coloca tu video como `input.mp4` en la raíz del proyecto y ejecuta:

```powershell
python -m vision_pipeline validate-config --config config/app.json
python -m vision_pipeline run --config config/app.json --source input.mp4
```

Salidas por defecto:

```
out/processed.mp4
out/frames.jsonl
out/metrics.json
out/frames/frm_000000.jpg ...
```

Opciones útiles:

```powershell
# Descripción para todos los frames
python -m vision_pipeline run --config config/app.json --source input.mp4 --description "seña 1"

# Guardar todos los frames como imagen
python -m vision_pipeline run --config config/app.json --source input.mp4 --frames all

# Solo métricas, sin escribir video
python -m vision_pipeline run --config config/app.json --source input.mp4 --no-video --frames none

# Benchmark de 300 frames (sin codificar video)
python -m vision_pipeline benchmark --config config/app.json --source input.mp4 --max-frames 300

# Esqueleto con manos/rostro (holistic)
python -m vision_pipeline run --config config/app_holistic.json --source input.mp4
```

## Arquitectura

```
Fuente (archivo/cámara)
  → hilo de captura (cola acotada, drop-oldest en vivo)
  → crop + resize + letterbox
  → copia de análisis (256×256) → MediaPipe Landmarker
  → filtros TensorFlow/OpenCV con máscara de persona
  → render del esqueleto configurado
  → video + JSONL + keyframes + métricas
```

Decisiones relevantes:

- MediaPipe consume la copia **sin difuminar** pero con la misma geometría que la
  salida, por lo que las coordenadas normalizadas coinciden 1:1 con el frame final.
- Los filtros se aplican antes de dibujar el esqueleto.
- Si no hay máscara, el gaussiano no difumina el frame completo (evita resultados
  accidentales); se emite un warning una sola vez.

## Configuración (`config/app.json`)

| Sección | Campos principales |
|---|---|
| `source` | `type` (`file`/`camera`), `path`, `index`, `target_fps`, `max_frames` |
| `crop` | `mode` (`center`/`rect`), `rect`, `aspect`, `output_size`, `letterbox` |
| `mask` | `provider` (`ellipse`/`pose_bbox`/`selfie_segmenter`), `every_n`, `smoothing`, `feather` |
| `landmarks` | `enabled`, `model` (`pose`/`holistic`), `analysis_size`, `smoothing`, `model_path` |
| `skeleton` | `enabled`, `path` |
| `filters` | lista ordenada de filtros |
| `output` | `video`, `jsonl`, `metrics`, `frames`, `every_n`, `description` |
| `runtime` | `queue_size`, `drop_policy`, `warmup_frames`, `min_fps`, `show` |

Los paths se resuelven relativos al directorio desde donde ejecutas el comando.

### Filtro gaussiano

```json
{
  "name": "gaussian",
  "enabled": true,
  "target": "background",
  "sigma": 10.0,
  "radius": null,
  "backend": "tensorflow"
}
```

- `target: "background"` resalta a la persona difuminando el fondo.
- `target: "person"` difumina a la persona (privacidad).
- `backend: "opencv"` permite una ruta de respaldo sin TensorFlow.
- `radius: null` calcula `ceil(3·sigma)`.

## JSON de esqueleto

`config/skeleton/pose_default.json` usa nombres legibles de los 33 landmarks de
pose. `config/skeleton/hands_lsec.json` usa pose + manos (`left_hand_0..20`,
`right_hand_0..20`) y requiere `landmarks.model: "holistic"`.

```json
{
  "version": 1,
  "source": "pose",
  "points": {
    "base": ["left_shoulder", "right_shoulder"],
    "highlight": ["left_wrist", "right_wrist"]
  },
  "connections": [["left_shoulder", "left_wrist"]],
  "styles": {
    "point": { "radius": 4, "color": [0, 255, 0] },
    "line": { "thickness": 2, "color": [255, 255, 255] },
    "highlight": { "radius": 7, "color": [0, 200, 255], "glow": true }
  },
  "min_visibility": 0.5
}
```

Los colores se escriben en **RGB** y se convierten internamente a BGR. Los nombres
se validan al cargar el JSON; un nombre desconocido produce un error explícito.

## Contrato de salida

Una línea de `frames.jsonl` por frame:

```json
{
  "schema_version": "1.0",
  "session_id": "ses_20261031T140322Z_a1b2c3d4",
  "frame_id": "frm_000012",
  "frame_index": 12,
  "timestamp_ms": 400.0,
  "timestamp_iso": "2026-10-31T14:03:22.400Z",
  "description": "",
  "source": {"type": "file", "path": "input.mp4", "width": 1920, "height": 1080, "fps": 30.0},
  "transform": {"crop": [420, 0, 1080, 1080], "output": [640, 640], "scale": 0.593, "pad": [0, 0]},
  "image": {"path": ".../out/frames/frm_000012.jpg", "width": 640, "height": 640},
  "landmarks": {
    "pose": [{"id": 0, "name": "nose", "x": 0.51, "y": 0.22, "z": -0.12, "visibility": 0.99}]
  },
  "skeleton": {"config": "config/skeleton/pose_default.json", "points_drawn": ["nose"], "connections_drawn": []},
  "filters": [{"name": "gaussian", "target": "background", "sigma": 10.0}],
  "metrics": {"process_ms": 41.2, "fps_rolling": 24.3}
}
```

Reglas:

- `frame_id` es único y coincide con el nombre de la imagen cuando se guarda.
- `frame_index` y `timestamp_ms` son monótonos.
- `description` siempre existe; por defecto `""`.
- `transform` permite reconstruir la posición en el video original.
- `metrics.json` resume la sesión: frames, FPS, p50/p95, descartes y cumplimiento
  de `runtime.min_fps`.

## Añadir filtros

1. Crea `src/vision_pipeline/filters/mi_filtro.py`.
2. Hereda de `VideoFilter`, declara `name` y decora con `@register_filter`.
3. Añade la entrada en `filters` de `app.json`.

```python
from .base import FilterContext, VideoFilter
from .registry import register_filter

@register_filter
class PersonGlow(VideoFilter):
    name = "person_glow"

    def apply(self, frame, context: FilterContext):
        # context.mask: float32 [0,1] a resolución de salida (1 = persona)
        return frame
```

El pipeline incorpora los filtros de forma dinámica (`filters/<name>.py`), sin
tocar `pipeline.py`. Filtros futuros previstos: `person_glow`, `edge_outline`,
`color_boost`, `zoom`, `mosaic_privacy`, `background_removal`.

## Rendimiento

Estrategias ya implementadas:

- Gaussiano separable (dos pasadas) en TensorFlow.
- Análisis de landmarks a 256×256 independiente de la salida (640×640 por defecto).
- Máscara de segmentación cada `mask.every_n` frames con suavizado temporal.
- Dibujo solo de los puntos/conexiones configurados.
- Hilo de captura con cola acotada y descarte del frame más viejo en vivo.
- Video escrito con OpenCV; `frames: keyframes` evita guardar imágenes por frame.

Usa `benchmark` y revisa `out/metrics.json`. Si no alcanzas 15 FPS:

1. Baja `landmarks.analysis_size` a `[192, 192]`.
2. Sube `mask.every_n` a `3` o usa `mask.provider: "ellipse"`.
3. Reduce `crop.output_size` a `[480, 480]`.
4. Usa `skeleton` con menos puntos.
5. En archivos, `source.target_fps: 15` descarta frames de entrada.

## Pruebas

```powershell
pytest
```

Las pruebas cubren geometría/letterbox, configuración, máscara y composición,
kernel gaussiano, JSON de esqueleto y contrato del registro. Las que dependen de
TensorFlow se omiten si no está instalado.

## Estructura

```
src/vision_pipeline/
├─ cli.py              # run / benchmark / validate-config
├─ config.py           # esquema y validación
├─ geometry.py         # crop, letterbox y mapeo
├─ capture.py          # hilo lector
├─ pipeline.py         # orquestación
├─ records.py          # contrato JSON
├─ metrics.py          # FPS y latencias
├─ filters/            # gaussiano, máscaras, registro
├─ landmarks/          # MediaPipe, suavizado, esquema
├─ render/             # esqueleto configurable
└─ io/                 # JSONL, video, imágenes
```

## Limitaciones actuales

- La integración con la app Android (TFLite/streaming móvil) queda fuera de esta fase.
- El modo `LIVE_STREAM` de MediaPipe no está implementado; se usa `VIDEO` síncrono
  para garantizar la correspondencia frame ↔ JSON.
- El video se escribe con OpenCV (`mp4v` por defecto); para H.264 puede requerirse
  un build de OpenCV con soporte o cambiar el `fourcc`.
