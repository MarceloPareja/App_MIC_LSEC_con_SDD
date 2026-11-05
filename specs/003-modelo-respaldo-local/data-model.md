# Data Model: Modelo de Respaldo Local LSEC

**Feature**: `003-modelo-respaldo-local`

## Entities

### 1. EstadoConexion
Representa el estado actual de la conectividad y el motor de inferencia activo.
- `id`: Identificador único del estado.
- `tipoServicio`: Enum (`NUBE`, `LOCAL`).
- `conectado`: Booleano (true si hay conexión con el servidor cloud).
- `mensajeAdvertencia`: String descriptivo (p. ej., "Usando modelo local de respaldo: la traducción puede ser más imprecisa").
- `timestamp`: Marca de tiempo del cambio de estado.

### 2. SolicitudTraduccionLocal
Estructura de entrada y salida para el modelo TFLite local (idéntica a la interfaz cloud).
- `requestId`: ID único de la solicitud.
- `clipDuration`: Duración del clip de video.
- `tensorEntrada`: Buffer o array de floats correspondiente a los fotogramas procesados de señas.
- `resultadoTexto`: Texto traducido resultante de la inferencia TFLite.
