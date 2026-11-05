# Research: Modelo de Respaldo Local LSEC

**Feature**: `003-modelo-respaldo-local`

## Technical Decisions & Rationale

### 1. Motor de Inferencia Local: TensorFlow Lite
- **Decision**: Utilizar TensorFlow Lite (`org.tensorflow:tensorflow-lite`) en el cliente Android.
- **Rationale**: Mantiene compatibilidad directa con el modelo en la nube (mismos tensores de entrada y salida), garantizando que el preprocesamiento de video/señas y la interpretación de resultados sean idénticos tanto para la nube como para el modo local.
- **Alternatives considered**: PyTorch Mobile (descartado por no alinearse con el stack TFLite de la nube), modelos basados en reglas (descartado por baja precisión).

### 2. Detección y Conmutación de Conexión
- **Decision**: Usar `ConnectivityManager` de Android combinado con un interceptor/observador en OkHttp/Retrofit.
- **Rationale**: Permite detectar de forma síncrona y reactiva la pérdida de conexión a internet o la falta de disponibilidad del servidor cloud, activando el procesador local TFLite en <2 segundos.
- **Alternatives considered**: Ping continuo por HTTP (descartado por alto consumo de batería y datos).

### 3. Notificación Visual al Usuario
- **Decision**: Banner superior o indicador de estado de red/modelo en la UI (`MainActivity` / `ChatActivity`).
- **Rationale**: Informa claramente al usuario cuando se está operando con el modelo de respaldo local y advierte sobre posibles limitaciones (menor precisión o mayor tiempo de procesamiento en videos grabados).
