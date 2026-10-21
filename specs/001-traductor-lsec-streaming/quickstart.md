# Quickstart Validation Guide: TraductorLSEC

**Feature**: Traductor de Lengua de Señas Ecuatoriana (TraductorLSEC)
**Date**: 2026-10-21

## Propósito
Esta guía documenta los escenarios de validación end-to-end para comprobar el funcionamiento correcto del streaming de video LSEC, la comunicación con el modelo TFLite en la nube, el historial de chat con límite de 30 elementos, la síntesis TTS y el manejo de baja conectividad.

## Prerrequisitos
1. Entorno de desarrollo Android (Android Studio / Gradle).
2. Dispositivo físico Android (API 24+) o emulador con soporte de cámara y TTS.
3. Conexión de red activa (o simulación de baja conectividad).

## Escenarios de Validación End-to-End

### 1. Validación de Permisos y Acceso a Cámara
- **Pasos**: Iniciar la aplicación en el dispositivo Android.
- **Resultado Esperado**: La app solicita permisos de cámara y audio. Al aceptarlos, se muestra la vista previa de la cámara en tiempo real sin errores.

### 2. Validación de Streaming y Traducción con TFLite Remoto
- **Pasos**: 
  1. Iniciar la transmisión de video desde la interfaz.
  2. Verificar en los logs o interceptor de red que los paquetes de video se envían vía POST multipart (`id_unico`, `duracion_clip_ms`, `video_chunk`).
  3. Comprobar que la respuesta del servidor se muestra en formato de chat tipo WhatsApp en menos de 2 segundos.
- **Resultado Esperado**: El texto traducido aparece en el chat en tiempo real.

### 3. Validación de Historial de Chat (Máximo 30 elementos)
- **Pasos**: Simular o insertar 31 mensajes de traducción consecutivos en la base de datos local Room.
- **Resultado Esperado**: El historial de chat purga automáticamente el mensaje más antiguo, manteniendo estrictamente un tamaño máximo de 30 elementos.

### 4. Validación de Síntesis de Voz (TTS)
- **Pasos**: Tocar sobre un mensaje traducido en el chat para reproducir su audio.
- **Resultado Esperado**: El motor TTS nativo de Android genera y reproduce el audio correspondiente en español.

### 5. Validación de Manejo de Baja Conectividad
- **Pasos**: Simular pérdida o degradación de la red (modo avión o throttling) durante una sesión de streaming activa.
- **Resultado Esperado**: La aplicación muestra una notificación intuitiva de estado de red ("Baja conexión, reintentando...") y reanuda el envío al restablecerse la señal, sin corromper el estado del chat.
