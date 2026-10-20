# Data Model: TraductorLSEC

**Feature**: `001-traductor-lsec`

## Entidades Principales

### 1. SolicitudTraduccion (Modelo / Entidad Local)
Representa una solicitud de traducción de video (en vivo o desde galería) almacenada localmente para gestión de red y reintentos.
- `id` (Long, Primary Key, Auto-generate)
- `rutaArchivoVideo` (String): Ruta local del archivo de video en el dispositivo.
- `duracionSegundos` (Long): Duración del video (máximo 600 segundos / 10 min).
- `estado` (String): Estado actual (`PENDIENTE`, `ENVIANDO`, `COMPLETADO`, `ERROR`).
- `fechaCreacion` (Long): Timestamp de creación de la solicitud.
- `intentos` (Int): Número de reintentos realizados ante baja conexión.

### 2. ResultadoTraduccion (DTO / Entidad de Respuesta)
Representa la respuesta recibida desde el modelo de deep learning en la nube (TFLite service).
- `idTraduccion` (String): Identificador único de la inferencia.
- `textoTraducido` (String): Texto resultante de la interpretación de LSEC.
- `audioUrl` (String o Base64): Recurso o datos de síntesis de voz (audio) de la traducción.
- `confianza` (Float): Nivel de confianza del modelo TFLite.
- `marcaTiempo` (Long): Timestamp de recepción del resultado.

### 3. ConfiguracionApp (Entidad de Preferencias)
- `usarAceleracionHardware` (Boolean): Habilitar delegados de hardware compatibles.
- `volumenAudio` (Float): Nivel de reproducción para la síntesis de voz.
