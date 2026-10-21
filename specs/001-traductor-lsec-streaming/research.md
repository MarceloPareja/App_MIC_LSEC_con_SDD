# Research: TraductorLSEC

**Feature**: Traductor de Lengua de Señas Ecuatoriana (TraductorLSEC)
**Date**: 2026-10-21

## 1. Captura y Streaming de Video por Paquetes en Android
- **Decision**: Utilizar CameraX API combinada con codificación de video en fragmentos (chunks) por lotes de tiempo o tamaño.
- **Rationale**: CameraX ofrece compatibilidad robusta desde Android 7.0+ (API 24+) y abstracción estable sobre el hardware de la cámara. El envío por paquetes evita almacenar clips largos de hasta 10 minutos en la memoria interna del dispositivo.
- **Alternatives Considered**: 
  - MediaRecorder tradicional: Más propenso a problemas de compatibilidad entre fabricantes de dispositivos Android.
  - Streaming WebRTC completo: Demasiada sobrecarga de infraestructura para un modelo basado en procesamiento por clip e inferencia TFLite remota.

## 2. Comunicación con Modelo TFLite en la Nube
- **Decision**: Arquitectura cliente-servidor HTTP POST con payload multipart/form-data o WebSocket ligero transmitiendo fragmentos de video acompañados de metadatos (`id_unico`, `duracion_clip`).
- **Rationale**: El modelo TFLite desplegado en la nube recibe los paquetes con ID único y duración exacta para realizar la inferencia y retornar el texto traducido en tiempo real.
- **Alternatives Considered**: Inferencia local con TFLite en el dispositivo móvil (descartado debido a los requisitos de hardware avanzados para modelos complejos de LSEC y la necesidad de actualización centralizada del modelo).

## 3. Historial de Chat y Almacenamiento Local (Room DB)
- **Decision**: SQLite local mediante Room Persistence Library con un disparador o política de purga automática para mantener estrictamente un máximo de 30 mensajes recientes.
- **Rationale**: Garantiza que no se acumulen datos innecesarios en el dispositivo, cumpliendo con la política de no requerir inicio de sesión ni almacenamiento persistente en la nube.
- **Alternatives Considered**: SharedPreferences (demasiado limitado para consultas estructuradas de chat) o archivos JSON planos (ineficientes para consultas y ordenamiento).

## 4. Síntesis de Voz (Text-to-Speech - TTS)
- **Decision**: Android native `TextToSpeech` engine configurado en idioma español (`es_EC` o `es_ES`).
- **Rationale**: Viene integrado en la plataforma Android, no requiere librerías externas pesadas y funciona de manera offline una vez descargado el paquete de voz del sistema.
- **Alternatives Considered**: APIs de TTS en la nube (descartadas por la dependencia de conectividad constante y latencia).

## 5. Resiliencia ante Baja Conectividad
- **Decision**: Cola de reintentos local con OkHttp Interceptor y manejo explícito de estados de red mediante `ConnectivityManager`.
- **Rationale**: Permite reintentar el envío de paquetes de video si hay fluctuaciones de señal, mostrando notificaciones intuitivas al usuario para evitar confusiones.
- **Alternatives Considered**: Bloquear la interfaz hasta recuperar conexión (rechazado por mala experiencia de usuario y falta de intuición).
