# Research: TraductorLSEC - Android Nativo & TFLite Cloud

**Feature**: `001-traductor-lsec`

## 1. Captura de Video con CameraX en Android
- **Decision**: Utilizar CameraX API de Android Jetpack.
- **Rationale**: CameraX ofrece compatibilidad nativa robusta desde Android 7.0 (API 24) en adelante, simplificando la gestión del ciclo de vida y garantizando soporte multidispositivo con la máxima aceleración de hardware disponible.
- **Alternatives considered**: Camera2 API (demasiado compleja y propensa a inconsistencias en fabricantes); bibliotecas de terceros (añaden dependencias innecesarias y peso al binario).

## 2. Inferencia y Procesamiento de Modelos TFLite Cloud
- **Decision**: Enviar videos grabados (hasta 10 min) o fragmentos de streaming a un servicio cloud que ejecuta el modelo TFLite, utilizando Retrofit con OkHttp (soporte de multipart upload y timeouts configurados).
- **Rationale**: Los videos de hasta 10 minutos superan la capacidad de procesamiento óptimo local en dispositivos de gama baja/media; delegar en la nube con un backend basado en TFLite garantiza alta precisión y compatibilidad universal con el hardware del cliente.
- **Alternatives considered**: Ejecución local completa de TFLite para modelos complejos de video de 10 min (consumo excesivo de batería y limitaciones de RAM en dispositivos Android económicos).

## 3. Manejo de Baja Conexión y Resiliencia
- **Decision**: Implementar una cola local de solicitudes utilizando Room Database y WorkManager para reintentos automáticos en segundo plano cuando la conectividad se restablezca.
- **Rationale**: Garantiza el cumplimiento del requisito de trabajo con baja conexión, evitando la pérdida de videos y reintentando la transmisión de manera inteligente sin intervención manual.
- **Alternatives considered**: Guardar únicamente en memoria RAM (se pierde si la app se cierra); reintentos sincrónicos bloqueantes (frustrantes para el usuario).

## 4. Arquitectura MVC y Estandarización en Español
- **Decision**: Estructurar el código en paquetes `controlador`, `modelo` y `vista` estrictamente en idioma español, cumpliendo los principios de la constitución del proyecto.
- **Rationale**: Mantiene el desacoplamiento cliente-servidor y asegura la conformidad absoluta con los estándares lingüísticos y arquitectónicos del proyecto.
- **Alternatives considered**: Patrones MVVM o MVP en inglés (desalineados con los mandatos constitucionales del proyecto).
