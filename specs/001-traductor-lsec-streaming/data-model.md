# Data Model: TraductorLSEC

**Feature**: Traductor de Lengua de Señas Ecuatoriana (TraductorLSEC)
**Date**: 2026-10-21

## Entidades Principales

### 1. MensajeTraduccion (Entity / Room Table)
Representa cada entrada en el historial de chat de traducciones.

| Campo | Tipo | Restricciones / Descripción |
|-------|------|-----------------------------|
| `id` | Long (PK) | Identificador único autoincremental en SQLite/Room. |
| `idUnicoClip` | String | Identificador único del streaming o clip de video asociado. |
| `textoTraducido` | String | Texto resultante de la traducción de LSEC devuelto por el modelo remoto. |
| `marcaTemporal` | Long | Epoch timestamp del momento en que se generó la traducción. |
| `estadoAudio` | String | Estado del TTS (`PENDIENTE`, `REPRODUCIDO`, `ERROR`). |

**Reglas de Negocio y Ciclo de Vida**:
- El historial se limita estrictamente a un máximo de 30 registros. Al insertar el registro número 31, se elimina automáticamente el registro más antiguo (FIFO).
- No se sincroniza ni se almacena ningún dato en servidores cloud de persistencia; todo el historial reside exclusivamente en la base de datos local del dispositivo.

### 2. SesionStreaming (Domain Model / Controller State)
Representa el estado activo de la captura de video desde la cámara.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `idUnico` | String (UUID) | UUID único generado al iniciar la sesión de transmisión. |
| `duracionClipMs` | Long | Duración acumulada del clip en milisegundos (máximo 10 minutos / 600,000 ms). |
| `estadoTransmision` | Enum | `INACTIVA`, `TRANSMITIENDO`, `PAUSADA_BAJA_CONEXION`, `FINALIZADA`. |
| `paquetesEnviados` | Int | Contador de paquetes de video enviados a la nube. |

**Reglas de Transición**:
- Al alcanzar los 10 minutos (600,000 ms), la sesión se finaliza automáticamente notificando al usuario.
- Si la conectividad cae, pasa a `PAUSADA_BAJA_CONEXION` intentando reintentos automáticos sin perder los metadatos del clip.
