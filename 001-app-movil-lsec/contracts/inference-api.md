# Contrato cliente ↔ servicio de inferencia LSEC

**Feature**: 001-app-movil-lsec | **Fecha**: 2026-10-20 | **Estado**: contrato de cliente (consumidor)

Este documento define lo que el cliente móvil **espera** del servicio de inferencia. El
servicio real es una feature separada y **no existe todavía** en este repositorio: el
cliente se desarrolla y se prueba contra el servidor simulado de `mock_server/`, que
implementa este mismo contrato.

- Implementación de referencia (simulada): `mock_server/server.dart`
- Consumidor en el cliente: `mobile/lib/data/remote/inference_client.dart`
- Mapeo de errores a mensajes: `mobile/lib/core/error/`

---

## 1. Superficie de la API

Base: `https://api.traductorlsec.ec` (configurable en `mobile/lib/core/config/`).
En desarrollo, el emulador Android alcanza el host en `http://10.0.2.2:8080`.

| Método | Ruta | Propósito | Éxito |
|---|---|---|---|
| `POST` | `/v1/translate` | Enviar una muestra de seña y obtener su traducción | `200` (síncrono) o `202` (proceso en curso) |
| `GET` | `/v1/translate/{requestId}` | Consultar un proceso devuelto como `202` | `200` |
| `GET` | `/v1/contract` | Descubrimiento de capacidades: formatos, tamaño y duración máximos, idiomas, versiones de modelo, umbral de confianza | `200` |

`GET /v1/contract` permite que el cliente lea los límites reales del servidor en lugar de
tenerlos codificados, algo especialmente útil mientras el servicio no está desplegado.

### 1.1 Código de idioma

- `ecs` = Lengua de Señas Ecuatoriana (ISO 639-3; Glottolog `ecua1243`).
- `es` = español.

---

## 2. Petición: `POST /v1/translate`

```http
POST /v1/translate HTTP/1.1
Host: api.traductorlsec.ec
Content-Type: multipart/form-data; boundary=----TraductorLSEC7f3a
Accept: application/json, application/problem+json
Authorization: Bearer <token-de-corto-vida>
Idempotency-Key: 9b1d2f5e-6a1c-4f1a-9c3e-7b2a5d8e4f10
X-Client-Version: 1.0.0
X-Client-Platform: android
X-Request-Id: 7c1e9a44-1f2b-4e88-9c10-2d5b6f8a0c31
```

**Parte 1 — `metadata`, `Content-Type: application/json`:**

```json
{
  "source_language": "ecs",
  "target_language": "es",
  "capture": {
    "duration_ms": 3200,
    "width": 1280,
    "height": 720,
    "frame_rate": 30,
    "video_codec": "h264",
    "audio_codec": "aac-lc",
    "sample_rate_hz": 48000,
    "audio_channels": 1,
    "size_bytes": 612345
  },
  "device": { "platform": "android", "app_version": "1.0.0" },
  "client_confidence_threshold": 0.5
}
```

**Parte 2 — `file`, `Content-Type: video/mp4`, `filename="clip.mp4"`:** bytes MP4, enviados
en streaming desde la caché privada de la aplicación (nunca desde el almacén multimedia
compartido).

### 2.1 Privacidad de la petición (FR-018)

La parte de metadatos **no** contiene identificador de usuario, nombre, correo, teléfono,
ubicación, identificador publicitario, IMEI ni número de serie. Se admite un
`install_id` aleatorio por instalación (UUID v4, reiniciable por la persona usuaria, no
derivado del hardware) para control de abuso, que debe documentarse como no identificante.
El cliente elimina los metadatos de ubicación (EXIF) y nunca escribe el clip en el
almacén compartido del dispositivo.

---

## 3. Respuesta de éxito: `200 OK`

```json
{
  "request_id": "tr_01JBXYZ8Z2K3M4N5P6Q7R8S9T0",
  "status": "completed",
  "outcome": "ok",
  "translation": {
    "text": "Buenos días, ¿cómo estás?",
    "confidence": 0.87,
    "source_language": "ecs",
    "source_language_confidence": 0.94,
    "target_language": "es"
  },
  "model": { "name": "lsec-es-ct2", "version": "2026-10-01", "pipeline_version": "3" },
  "timing": {
    "received_at": "2026-10-20T18:44:02.113Z",
    "completed_at": "2026-10-20T18:44:04.902Z",
    "server_processing_ms": 2710,
    "queue_wait_ms": 180
  },
  "sample": { "duration_ms": 3200, "size_bytes": 612345 },
  "warnings": []
}
```

| Campo | Tipo | Obligatorio | Uso en el cliente |
|---|---|---|---|
| `request_id` | string | sí | Identificador opaco; se correlaciona con el `Idempotency-Key` y se guarda en el historial |
| `status` | enum `completed` | sí | Marca terminal de éxito |
| `outcome` | enum `ok` \| `low_confidence` \| `unexpected_language` | sí | **Resultado de dominio, no estado de transporte.** Punto único de decisión para FR-012 y FR-013 |
| `translation.text` | string | sí | Texto traducido; se muestra literal (FR-004) |
| `translation.confidence` | float 0.0–1.0 | sí | Confianza del modelo sobre la traducción completa |
| `translation.source_language_confidence` | float 0.0–1.0 | no | Confianza de que la entrada era realmente LSEC |
| `translation.target_language` | string | sí | Idioma real de la salida; si difiere del solicitado, el `outcome` es `unexpected_language` |
| `model.name` / `.version` / `.pipeline_version` | string | sí | Modelo que produjo el resultado; permite diagnóstico de regresiones |
| `timing.server_processing_ms` | int | sí | Tiempo de inferencia del servidor; distingue "servicio lento" de "subida lenta" |
| `timing.queue_wait_ms` | int | no | Tiempo en cola del servidor |
| `sample.duration_ms`, `sample.size_bytes` | int | no | Eco de lo que el servidor recibió tras validarlo |
| `warnings` | string[] | sí (puede estar vacío) | Banderas no fatales: `LOW_CONFIDENCE`, `UNEXPECTED_LANGUAGE`, `LOW_LIGHT`, `AUDIO_NOISY`, `PARTIAL_RESULT` |

### 3.1 Confianza baja e idioma inesperado son **resultados, no errores HTTP**

La petición **funcionó**: se aceptó un video, se procesó y se produjo una traducción. Un
`422` por confianza baja mezclaría "la entrada es inválida" con "el modelo no está
seguro", y rompería las herramientas que leen códigos de estado (CDN, gateway, balanceador,
librerías de reintento). Por eso:

- `422` significa que **la muestra** es incorrecta → toca regrabar.
- `200` con `outcome: low_confidence` significa que **el resultado** es débil → se ofrece
  regrabar, nunca se reintenta automáticamente (el mismo clip produce la misma confianza).

El cliente decide con un único enumerado `TranslationErrorCode` en `core/error/`, que
cubre tanto los sobres de error HTTP como los `outcome` de éxito.

---

## 4. Respuesta de error: RFC 9457 Problem Details

Todos los errores 4xx/5xx usan `Content-Type: application/problem+json`.

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/problem+json
Retry-After: 5
X-Request-Id: 7c1e9a44-1f2b-4e88-9c10-2d5b6f8a0c31
```

```json
{
  "type": "https://api.traductorlsec.ec/errors/service-unavailable",
  "title": "Inference service unavailable",
  "status": 503,
  "detail": "The inference pipeline is temporarily saturated. The captured clip was not processed.",
  "instance": "/v1/translate/tr_01JBXYZ8Z2K3M4N5P6Q7R8S9T0",
  "code": "SERVICE_UNAVAILABLE",
  "request_id": "tr_01JBXYZ8Z2K3M4N5P6Q7R8S9T0",
  "retryable": true,
  "retry_after_seconds": 5,
  "documentation_url": "https://docs.traductorlsec.ec/errors/SERVICE_UNAVAILABLE"
}
```

| Miembro | Tipo | Uso |
|---|---|---|
| `code` | string | **Código estable legible por máquina.** Último segmento de `type`. Es el campo por el que bifurca el cliente. Un `code` publicado no se renombra ni se reutiliza: es un cambio incompatible |
| `retryable` | bool | Veredicto del servidor. El cliente reintenta solo si `retryable` **y** su propia política lo permiten |
| `retry_after_seconds` | int \| null | Refleja la cabecera `Retry-After`; el cliente prefiere la cabecera |
| `request_id` | string | Correlación con soporte; se muestra en la acción de reportar problema |
| `errors[]` | array | Detalle por campo para validaciones `422` (`field`, `code`, `message`, `actual`, `limit`) |

### 4.1 Tabla de códigos de error

`Auto` = el cliente reintenta solo. `Usuario` = el cliente ofrece un botón de reintento.
Nunca ambos a la vez, salvo excepción indicada.

| `code` | HTTP | Significado | Mensaje al usuario (intención) | Auto | Usuario | Acción del cliente |
|---|---|---|---|---|---|---|
| `SERVICE_UNAVAILABLE` | 503 | Servicio caído, saturado o en mantenimiento | "El servicio no está disponible en este momento. Tu muestra se guardó; puedes reintentar en un momento." | ✔ (≤2) | ✔ | Conserva la muestra; reintenta con la **misma** `Idempotency-Key`; respeta `Retry-After` |
| `TIMEOUT` | 504 | Se agotó el plazo del servidor o el del cliente | "El servicio tardó demasiado en responder. Vuelve a intentarlo con la misma grabación." | ✔ (≤2) | ✔ | Misma muestra, misma clave. El timeout del cliente se reporta con este mismo código |
| `INTERNAL_ERROR` | 500 | Fallo no controlado del servicio | "Algo falló al procesar tu seña. Vuelve a intentarlo." | ✔ (1) | ✔ | Misma muestra, misma clave. Agotados los intentos, mensaje genérico y acción de reportar |
| `RATE_LIMITED` | 429 | Demasiadas peticiones | "Has hecho demasiadas traducciones seguidas. Espera unos segundos." | ✔ (1) | ✔ | Respeta `Retry-After` exactamente; no reenvía antes |
| `NETWORK_ERROR` | — (cliente) | Fallo de socket/DNS/TLS durante el envío | "Se perdió la conexión durante el envío. Tu grabación se conservó." | ✔ (al reconectar) | ✔ | Conserva la muestra en disco; reenvía con la misma clave al recuperar conexión |
| `CLIENT_OFFLINE` | — (cliente) | Sin conectividad al enviar | "No tienes conexión. Graba cuando tengas señal o activa los datos móviles." | ✘ | ✔ (al tener red) | No inicia el envío; conserva la muestra y reanuda solo al reconectar |
| `UNSUPPORTED_FORMAT` | 415 | Contenedor/codec no aceptado | "El formato de la grabación no es compatible. Vuelve a grabar con la cámara de la aplicación." | ✘ | ✔ ( regrabar ) | Nunca reintenta solo; el cliente puede re-encodar localmente |
| `SAMPLE_TOO_SHORT` | 422 | Duración menor al mínimo (1.5 s) | "La grabación fue muy corta. Mantén la seña al menos 2 segundos." | ✘ | ✔ ( regrabar ) | Nunca reintenta solo; exige regrabar |
| `SAMPLE_TOO_LONG` | 422 | Duración mayor al máximo (10 s) | "La grabación fue demasiado larga. Graba solo la frase que quieras decir." | ✘ | ✔ ( regrabar ) | Nunca reintenta solo |
| `SAMPLE_TOO_LARGE` | 413 | Tamaño por encima del límite (25 MB) | "El archivo de video es demasiado grande. Baja la calidad de la grabación." | ✘ | ✔ ( regrabar ) | El cliente debería detectarlo antes de enviar (§6) |
| `NO_AUDIO_TRACK` | 422 | El clip no tiene pista de audio (es obligatoria) | "La grabación no tiene audio. Revisa el permiso del micrófono." | ✘ | ✔ ( regrabar ) | Regrabar con audio |
| `CORRUPT_SAMPLE` | 422 | Contenedor ilegible o error de decodificación | "No pudimos leer la grabación. Graba de nuevo, poco a poco." | ✘ | ✔ ( regrabar ) | Nunca reintenta solo |
| `LOW_CONFIDENCE` | **200** (outcome) | Confianza del modelo por debajo del umbral | "La traducción es poco fiable. Repite la seña para mayor certeza." | ✘ | ✔ ( regrabar ) | Muestra el texto **con** la marca visible de "poco fiable" (FR-012, SC-007). Nunca reintenta solo |
| `UNEXPECTED_LANGUAGE` | **200** (outcome) | Idioma del resultado distinto del solicitado | "El resultado está en inglés, no en español." | ✘ | ✔ ( regrabar ) | Muestra el texto e indica el idioma detectado (FR-013); nunca oculta el texto |

---

## 5. Política de resiliencia del cliente

| Aspecto | Valor |
|---|---|
| Timeout de conexión | 15 s |
| Timeout de lectura | 60 s (margen sobre los 10 s de SC-001 para procesar y descargar) |
| Reintentos automáticos | 2 para `SERVICE_UNAVAILABLE` y `TIMEOUT`; 1 para `INTERNAL_ERROR` y `RATE_LIMITED`; 0 para el resto |
| Espera entre reintentos | Retroceso exponente, respetando `Retry-After`; base 1 s, techo 10 s, con jitter |
| Idempotencia | La misma muestra reenviada conserva la `Idempotency-Key`; el servidor no debe procesarla dos veces |
| Conexión perdida a mitad del envío | La muestra se conserva en caché privada; el reenvío usa la misma clave |
| Sin conexión al iniciar | No se inicia el envío; la acción de reintento queda habilitada y el cliente reanuda solo al recuperar la red |
| Muestra para regrabar | Nunca se reintenta automáticamente: la causa es la calidad de la muestra, no la red |
| Proceso `202` | Se consulta `GET /v1/translate/{requestId}` con espera creciente hasta un máximo de 60 s; al agotarse se reporta `TIMEOUT` |

---

## 6. Restricciones de la muestra que el cliente aplica antes de enviar

| Restricción | Valor por defecto | Origen |
|---|---|---|
| Duración mínima | 1.5 s | `SAMPLE_TOO_SHORT` |
| Duración máxima | 10 s | `SAMPLE_TOO_LONG` |
| Tamaño máximo | 25 MB | `SAMPLE_TOO_LARGE` |
| Contenedor | MP4 (H.264 + AAC-LC) | `UNSUPPORTED_FORMAT` |
| Frecuencia de muestreo de audio | 48 kHz, mono | `UNSUPPORTED_FORMAT` |
| Tasa de bits objetivo | 0.5–3 MB por clip | Restricción de SC-001 (ver §7) |

El cliente valida estas restricciones **antes** de iniciar la subida y muestra el mensaje
correspondiente, de modo que el caso normal de rechazo no depende de la red.

---

## 7. Restricción crítica: la calidad de captura la fija el cliente

SC-001 exige el texto en pantalla en menos de 10 s. Un clip de 20 MB no se puede subir ni
procesar en 10 s sobre una conexión de 3 Mbps (20 MB ≈ 53 s solo de subida). El servicio no
puede corregirlo: **el cliente debe capturar con una tasa de bits que deje el clip entre
0.5 y 3 MB**.

Consecuencias de diseño:

1. La configuración de captura fija resolución y tasa de bits, y el tamaño se valida antes
   de enviar (§6).
2. La captura se detiene automáticamente al alcanzar la duración máxima, para no producir
   clips que el servicio rechazaría.
3. El envío se hace en streaming desde la caché privada, con progreso real en bytes, para
   el estado "enviando" de FR-003.

---

## 8. Versionado del contrato

- Las rutas llevan versión explícita (`/v1/...`).
- El cliente envía `X-Client-Version`; el servidor responde con `model.pipeline_version`.
- Ante una versión mayor del servidor, el cliente sigue operando con la versión `v1` hasta
  que exista una implementación de la nueva versión: no se degradan silenciosamente
  functionalities.
- Los `code` de error publicados no se renombran ni se reutilizan con otro significado.
