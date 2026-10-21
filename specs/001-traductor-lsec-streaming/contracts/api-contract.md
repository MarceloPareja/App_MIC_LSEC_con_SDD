# API Contract: Cloud Deep Learning Model (TFLite Backend)

**Feature**: Traductor de Lengua de Señas Ecuatoriana (TraductorLSEC)
**Date**: 2026-10-21

## Endpoint de Traducción de Video por Paquetes

- **Método HTTP**: `POST`
- **Content-Type**: `multipart/form-data`
- **Descripción**: Envía paquetes de video de streaming capturados por la cámara junto con metadatos de duración y ID único para inferencia en el modelo TFLite desplegado en la nube.

### Parámetros de Solicitud (Request Form-Data)

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `id_unico` | String (UUID) | Sí | Identificador único de la sesión de streaming o clip. |
| `duracion_clip_ms` | Long | Sí | Duración en milisegundos del clip de video que comprende el paquete. |
| `video_chunk` | File (Binary) | Sí | Paquete binario de video (formato MP4/WebM codificado). |

### Respuesta Exitosa (Response 200 OK - JSON)

```json
{
  "id_unico": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "estado": "EXITO",
  "texto_traducido": "Hola, ¿cómo estás?",
  "marca_temporal": 1761062400000
}
```

### Respuesta de Error (Response 400 / 500 - JSON)

```json
{
  "id_unico": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "estado": "ERROR",
  "codigo_error": "CLIP_EXCEEDE_LIMIT",
  "mensaje": "La duración del clip excede el límite máximo de 10 minutos."
}
```
