# Data Model: App móvil cliente para la traducción de LSEC

**Feature**: 001-app-movil-lsec | **Fecha**: 2026-10-20 | **Fase**: 1 (Design)

Modelado de los datos que maneja el cliente móvil. Las entidades derivan de la
especificación (`spec.md`, sección *Key Entities*); los límites numéricos, de formato y de
retención derivan del contrato (`contracts/inference-api.md`) y de las decisiones de
investigación (`research.md`, D-3, D-4, D-7).

---

## 1. Diagrama de entidades

```text
┌─────────────────────────┐        ┌──────────────────────────┐
│ Muestra de seña         │        │ Traducción               │
│ (efímera, no persiste)  │───────▶│ (persiste en el dispositivo)│
└─────────────────────────┘        └───────────┬──────────────┘
       captura                                  │ pertenece
                                              ▼
                                    ┌──────────────────────────┐
                                    │ Historial de traducciones │
                                    │ (colección ordenada)      │
                                    └──────────────────────────┘

┌──────────────────────────┐
│ Preferencias de          │  gobierna la reproducción de
│ reproducción             │──────────▶ Traducción
└──────────────────────────┘
```

Relaciones:

- Una **Muestra de seña** produce como máximo una **Traducción**; la muestra no se
  conserva una vez procesada.
- Una **Traducción** pertenece a exactamente un **Historial de traducciones** y puede
  tener cero o varias reproducciones de voz asociadas (las reproducciones no se persisten).
- Las **Preferencias de reproducción** se aplican a todas las traducciones y se guardan
  localmente.

---

## 2. Muestra de seña

Representa la captura audiovisual de la seña. **Entidad efímera**: existe en memoria y en
el directorio temporal de la aplicación entre la captura y el borrado, y nunca se
persiste en el historial.

| Campo | Tipo | Obligatorio | Restricción |
|---|---|---|---|
| `path` | String | sí | Ruta absoluta dentro del directorio temporal de la aplicación. Nunca en el almacén compartido ni en los documentos de la app |
| `durationMs` | int | sí | "Duración mínima 1.5 s" y "Duración máxima 10 s" (`contracts/inference-api.md` §6) |
| `sizeBytes` | int | sí | "Tamaño máximo 25 MB" (`contracts/inference-api.md` §6) |
| `width` | int | sí | Resolución horizontal en píxeles |
| `height` | int | sí | Resolución vertical en píxeles |
| `frameRate` | int | sí | Fotogramas por segundo de la captura |
| `videoCodec` | String | sí | "Contenedor: MP4 (H.264 + AAC-LC)" (`contracts/inference-api.md` §6) |
| `audioCodec` | String | sí | "AAC-LC" según el contrato; la pista de audio es obligatoria |
| `sampleRateHz` | int | sí | "Frecuencia de muestreo de audio: 48 kHz, mono" (`contracts/inference-api.md` §6) |
| `hasAudioTrack` | bool | sí | Debe ser `true`; si no, el envío falla con `NO_AUDIO_TRACK` |
| `capturedAt` | DateTime | sí | Momento de la captura, en UTC |

### Reglas de validación (antes de enviar)

- `durationMs` debe estar entre 1500 y 10000; fuera de rango, la persona usuaria recibe el
  mensaje de regrabar (`SAMPLE_TOO_SHORT` / `SAMPLE_TOO_LONG`).
- `sizeBytes` no debe superar 26214400 (25 MB); en caso contrario, `SAMPLE_TOO_LARGE`.
- `hasAudioTrack` debe ser `true`; en caso contrario, `NO_AUDIO_TRACK`.
- La tasa de bits de captura se ajusta para que el clip quede entre 0,5 MB y 3 MB
  (`research.md`, D-3). Un clip de 20 MB no cabe en el presupuesto de 10 s de SC-001.
- Al terminar la operación (envío correcto, error o cancelación), el archivo se borra en
  un bloque `finally` y se limpia cualquier miniatura asociada.

### Transiciones de estado

```text
idle ──(iniciar captura)──▶ capturing ──(detener)──▶ captured ──(enviar)──▶ uploading
                                                                          │
capturing ──(cancelar)──▶ discarded (se borra el archivo temporal)        │
                                                                          ▼
                                                              ┌───────────────────┐
                                                              │  translating      │
                                                              └───────┬───────────┘
                                                                      │
                        ┌─────────────────────┬───────────────────────┴──────────────┐
                        ▼                     ▼                                      ▼
                   succeeded              failed                            failed_offline
              (se guarda la            (muestra          (sin red: se conserva la
               traducción en el         descartada,       muestra y se reintenta
               historial)               se informa)       al recuperar conexión)
```

---

## 3. Traducción

Unidad central del producto: el texto traducido con su contexto. Es lo que la aplicación
muestra, conserva y reproduce.

| Campo | Tipo | Obligatorio | Restricción |
|---|---|---|---|
| `id` | String | sí | UUID v4 generado en el cliente; clave primaria |
| `text` | String | sí | Texto traducido tal cual lo devuelve el servicio. Sin valor por defecto y sin truncado en la interfaz |
| `sourceLanguage` | String | sí | Código ISO 639-3 del idioma de entrada; `ecs` (Lengua de Señas Ecuatoriana) en la v1 |
| `targetLanguage` | String | sí | Código ISO 639-3 del idioma de salida; `es` en la v1. Si difiere del solicitado, el resultado es `unexpected_language` |
| `confidence` | double | sí | Confianza del modelo, en el rango 0.0–1.0. Por debajo del umbral (0,5 por defecto) el resultado se marca como poco fiable |
| `outcome` | enum | sí | `ok` \| `low_confidence` \| `unexpected_language`. Determina la marca visible en la interfaz |
| `requestId` | String | sí | Identificador opaco del servicio (`request_id`). Permite correlación con soporte y con los reintentos idempotentes |
| `modelVersion` | String | no | Versión del modelo que produjo el resultado (`model.version`) |
| `createdAt` | DateTime | sí | Fecha y hora de generación, en UTC, epoch en milisegundos |
| `warnings` | List\<String\> | sí | Banderas no fatales: `LOW_CONFIDENCE`, `UNEXPECTED_LANGUAGE`, `LOW_LIGHT`, `AUDIO_NOISY`, `PARTIAL_RESULT`. Puede estar vacía, nunca es nula |

### Reglas de validación

- `confidence` debe estar en el rango 0.0–1.0; fuera de rango, el resultado se trata como
  inválido y se informa con el mensaje genérico de fallo.
- `text` vacío o compuesto solo por espacios se considera un resultado inválido y no se
  guarda en el historial.
- Un `outcome` distinto de `ok` **no impide** guardar la traducción: se guarda con su
  marca visible, porque la persona usuaria decide si le sirve.

### Estados de reproducción

La reproducción de voz no es un estado de la entidad persistida, sino de la sesión de
interfaz: `idle` → `speaking` → `idle` (o `stopped` por interrupción del usuario o del
sistema). La traducción conserva `text`, de modo que volver a reproducirla no requiere
la captura original.

---

## 4. Historial de traducciones

Colección ordenada de las traducciones conservadas en el dispositivo. Permite consultar,
buscar y reproducir resultados anteriores, incluso sin conexión.

| Campo | Tipo | Obligatorio | Restricción |
|---|---|---|---|
| `id` | String | sí | UUID v4; clave primaria |
| `text` | String | sí | Texto traducido, sin truncar |
| `sourceLang` | String | sí | `ecs` en la v1 |
| `targetLang` | String | sí | `es` en la v1 |
| `confidence` | double | sí | Rango 0.0–1.0 |
| `outcome` | String | sí | `ok` \| `low_confidence` \| `unexpected_language` |
| `createdAt` | int | sí | Epoch en milisegundos, UTC. Es la clave de orden y de búsqueda por fecha |
| `requestId` | String | no | Correlación con el servicio. No contiene información personal |

### Esquema SQL

```sql
CREATE TABLE history (
  id           TEXT    PRIMARY KEY,
  text         TEXT    NOT NULL,
  source_lang  TEXT    NOT NULL,
  target_lang  TEXT    NOT NULL,
  confidence   REAL    NOT NULL,
  outcome      TEXT    NOT NULL,
  created_at   INTEGER NOT NULL,
  request_id   TEXT
);

CREATE INDEX idx_history_created_at ON history(created_at DESC);
```

### Reglas de retención, consulta y borrado

- **Retención máxima**: 200 entradas. Al insertar y superar el máximo, se borran las
  entradas más antiguas por `created_at` ascendente, dentro de una transacción.
- **Orden de consulta**: `created_at` descendente (más reciente primero).
- **Búsqueda por texto**: `LIKE %consulta%` sobre `text`; suficiente para 200 entradas.
- **Búsqueda por fecha**: rango de `created_at` con el índice `idx_history_created_at`.
- **Borrado individual**: borra la fila y su registro asociado de manera verificable.
- **Borrado total**: pide confirmación explícita, ejecuta `DELETE` de todas las filas,
  ejecuta `VACUUM` para recuperar espacio, limpia las cachés en memoria y deja el conteo en
  cero. La operación no se puede deshacer.
- **Cifrado**: la base se cifra con SQLCipher y la clave reside en el almacén de claves
  del plataforma; nunca en preferencias sin cifrar. La base se excluye de las copias de
  seguridad automáticas.

---

## 5. Preferencias de reproducción

Ajustes locales que gobiernan cómo se reproduce la voz de las traducciones.

| Campo | Tipo | Obligatorio | Valor por defecto | Restricción |
|---|---|---|---|---|
| `voiceEnabled` | bool | sí | `true` | Si es `false`, el botón de reproducción se oculta y el texto sigue disponible |
| `autoSpeak` | bool | sí | `false` | Si es `true`, la traducción se lee en voz al mostrarse; el usuario puede detenerla de inmediato |
| `locale` | String | sí | `es-EC` | Locales admitidos en orden de preferencia: `es-EC` → `es-MX` → `es-US` → `es-ES` → cualquier `es-*` |
| `speechRate` | double | sí | `1.0` | Rango 0,5–2,0 |
| `pitch` | double | sí | `1.0` | Rango 0,5–2,0 |
| `volume` | double | sí | `1.0` | Rango 0,0–1,0 |

### Reglas

- La resolución de la voz es una cadena de reserva: se prueba `es-EC` y, si el motor no la
  ofrece, se desciende por la lista hasta encontrar una voz disponible.
- Si no existe ninguna voz `es-*`, la aplicación no falla: deshabilita la reproducción con
  una explicación y mantiene operativo el texto.
- Las preferencias se guardan localmente y no se sincronizan ni se envían al servicio.

---

## 6. Modelo de datos del servicio de inferencia (referencia, no persistido)

El cliente no persiste estas estructuras más allá de la petición, pero debe modelarlas
para deserializar la respuesta (`contracts/inference-api.md` §3).

| Estructura | Campos |
|---|---|
| `TranslationResponse` | `request_id`, `status`, `outcome`, `translation{...}`, `model{name, version, pipeline_version}`, `timing{received_at, completed_at, server_processing_ms, queue_wait_ms}`, `sample{duration_ms, size_bytes}`, `warnings[]` |
| `Translation` | `text`, `confidence`, `source_language`, `source_language_confidence`, `target_language` |
| `ProblemDetails` | `type`, `title`, `status`, `detail`, `instance`, `code`, `request_id`, `retryable`, `retry_after_seconds`, `documentation_url`, `errors[]` |
| `ContractInfo` (`GET /v1/contract`) | formatos aceptados, tamaño y duración máximos, idiomas admitidos, versiones de modelo, umbral de confianza |

---

## 7. Datos que nunca se persisten ni se transmiten

| Dato | Motivo | Mecanismo de garantía |
|---|---|---|
| Muestra audiovisual de la seña | FR-017: no retener el video | Escritura solo en el directorio temporal; borrado en `finally`; prueba que verifica que no quedan archivos de video tras el flujo |
| Identificadores personales | FR-018: no enviar información identificable | La petición no incluye nombre, correo, teléfono, ubicación, identificador publicitario ni número de serie |
| Texto traducido en los registros | Privacidad | Los registros solo incluyen `request_id`, `outcome`, `confidence`, `timing.*`, `code` y estado HTTP |
| Ubicación (EXIF) de la captura | Privacidad | Se eliminan los metadatos de ubicación antes de enviar |
| Clave de cifrado de la base | Seguridad | Reside en el almacén de claves de la plataforma, nunca en preferencias sin cifrar |
