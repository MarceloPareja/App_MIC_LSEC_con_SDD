# Quickstart Validation Guide: TraductorLSEC

**Feature**: `001-traductor-lsec`

## Propósito
Esta guía documenta los escenarios de validación de principio a fin para certificar el correcto funcionamiento de la aplicación móvil TraductorLSEC.

## Prerrequisitos
1. Entorno de desarrollo Android Studio (Hedgehog o superior) instalado.
2. Dispositivo físico Android (API 24+) con cámara operativa o emulador con soporte de cámara virtual.
3. Conexión a internet (o simulación de red intermitente).

## Escenarios de Validación End-to-End

### 1. Validación de Grabación en Vivo y Traducción (P1)
1. Iniciar la aplicación TraductorLSEC (sin inicio de sesión requerido).
2. Conceder permisos de cámara cuando se solicite.
3. Presionar el botón de grabación en vivo para capturar un segmento de prueba de señas (máximo 10 minutos).
4. Detener la grabación y verificar el envío automático al servicio cloud TFLite.
5. **Resultado esperado**: La interfaz muestra en tiempo real el texto traducido y reproduce el audio correspondiente en menos de 5 segundos.

### 2. Validación de Selección de Video Previo desde Galería (P2)
1. Abrir la pantalla de selección de archivo en la aplicación.
2. Seleccionar un video existente en la galería del dispositivo (duración $\le$ 10 minutos).
3. Enviar el archivo.
4. **Resultado esperado**: Procesamiento exitoso y visualización de la traducción en texto y audio.

### 3. Validación de Resiliencia ante Baja Conexión (P3)
1. Activar el modo avión o simular red lenta/intermitente en el dispositivo.
2. Intentar enviar una solicitud de traducción de video.
3. **Resultado esperado**: La aplicación almacena la solicitud en la cola local (Room) y notifica el estado de red.
4. Desactivar el modo avión (restablecer conexión).
5. **Resultado esperado**: El sistema reintenta automáticamente la transmisión y completa la traducción exitosamente.
