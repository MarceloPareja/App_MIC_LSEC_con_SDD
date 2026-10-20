# API Contract: TraductorLSEC Cloud TFLite Service

**Feature**: `001-traductor-lsec`

## Endpoint de Traducción de Video

- **URL**: `/api/v1/traducir`
- **Método**: `POST`
- **Tipo de Contenido**: `multipart/form-data`

### Parámetros de Entrada (Request)
- `video`: Archivo binario de video (formatos soportados: MP4, MKV; duración máxima: 10 minutos / 600 segundos).
- `metadatos`: Objeto JSON con información del cliente (opcional, sin datos personales).

### Respuesta Exitosa (Response 200 OK)
```json
{
  "idTraduccion": "uuid-123456789",
  "estado": "EXITOSO",
  "textoTraducido": "Hola, ¿cómo estás?",
  "audioBase64": "UklGRi...",
  "confianza": 0.96,
  "marcaTiempo": 1729432800000
}
```

### Respuesta de Error (Response 400 / 422 / 500)
```json
{
  "codigoError": "VIDEO_EXCEDE_LIMITE",
  "mensaje": "El video excede la duración máxima permitida de 10 minutos."
}
```
