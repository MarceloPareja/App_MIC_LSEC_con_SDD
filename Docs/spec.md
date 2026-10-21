# Feature Specification: TraductorLSEC App Móvil

**Feature Branch**: `002-traductor-lsec-movil`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "La app móvil TraductorLSEC permitirá que una persona que no conoce lengua de señas ecuatoriana (LSEC) pueda comprender a una persona sorda que si la conozca, al enviar un video de las señas con máximo de 10 min en un streaming del video constante por paquetes para no consumir espacio del dispositivo innecesario. La aplicación debe tener acceso completo a la cámara para esta función. El video será procesado por un modelo de deep learning externo desplegado en la nube que necesitara la duración del clip enviado para el procesamiento e id unico, que devolverá en tiempo real la traducción de las señas en forma de texto en un chat con historial hasta 30 ultimas traducciones en un chat tipo respuesta whatsapp y un tts ayudara en el cliente movil generar el audio audio con los permisos para esto. La aplicación debe ser altamente intuitiva y fácil de usar; el manejo de errores es clave para evitar confusiones o malentendidos por parte del usuario. Debe tener la capacidad de trabajar con baja conexión. La app no necesita de un inicio de sesión ya que no guarda datos en la nube, solo usa el modelo remoto para procesar."

## Clarifications

### Session 2026-10-21

- Q: ¿La captura se envía manualmente? → A: Se envía constantemente mientras el botón de grabar esté encendido, traduciéndose en tiempo real.
- Q: ¿Qué ocurre con baja conexión, errores y permisos? → A: Con baja conexión se limita el TTS; los errores se manejan con mensajes específicos; sin permisos de audio/cámara la app se cierra hasta concederlos.
- Q: ¿La grabación continua puede superar los 10 minutos? → A: Sí, la referencia de 10 minutos no limita la grabación continua.
- Q: ¿Qué es un clip? → A: Una sección de video organizable con timestamp obtenido por el servidor.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capturar y enviar señas para traducción (Priority: P1)

Un usuario que no conoce LSEC abre la app, apunta la cámara hacia una persona sorda que realiza señas, y mientras el botón de grabar está encendido el video se envía constantemente por paquetes, traduciéndose en tiempo real.

**Why this priority**: Es la funcionalidad central del producto; sin ella no hay valor.

**Independent Test**: Puede probarse manteniendo el botón de grabar activo y verificando que las traducciones aparecen en tiempo real en el chat.

**Acceptance Scenarios**:

1. **Given** la app tiene permisos de cámara, **When** el usuario activa el botón de grabar, **Then** el video se envía constantemente por paquetes sin almacenarse localmente.
2. **Given** el botón de grabar activo, **When** llegan paquetes, **Then** la traducción en texto aparece en el chat en tiempo real.

---

### User Story 2 - Historial de traducciones en chat (Priority: P2)

El usuario visualiza las últimas 30 traducciones en un chat estilo WhatsApp para consultarlas posteriormente.

**Why this priority**: Permite consultar traducciones pasadas y mantener contexto de la conversación.

**Independent Test**: Puede probarse enviando más de 30 traducciones y verificando que solo se conservan las últimas 30.

**Acceptance Scenarios**:

1. **Given** existen traducciones previas, **When** se abre el chat, **Then** se muestran hasta las últimas 30 traducciones.
2. **Given** más de 30 traducciones, **When** llega una nueva, **Then** la más antigua se elimina del historial.

---

### User Story 3 - Reproducir audio de la traducción (TTS) (Priority: P3)

El usuario puede escuchar la traducción mediante síntesis de voz en el dispositivo, con los permisos de audio correspondientes.

**Why this priority**: Mejora la accesibilidad para usuarios que prefieren audio.

**Independent Test**: Puede probarse reproduciendo el audio de una traducción y verificando que se escucha correctamente.

**Acceptance Scenarios**:

1. **Given** una traducción en texto, **When** el usuario activa TTS, **Then** se reproduce el audio con los permisos de audio concedidos.

---

### Edge Cases

- Qué pasa cuando la conexión es baja o intermitente: se limita el TTS.
- En 10 minutos de video continuo la app debe seguir funcionando.
- Si existen errores, se maneja con un mensaje "no fue posible traducir/error conexión con el servidor/archivo no fue posible procesar".
- Si faltan permisos de audio o cámara, la app se cierra automáticamente hasta que el usuario conceda dichos permisos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La app MUST permitir capturar video de señas con la cámara del dispositivo.
- **FR-002**: La app MUST enviar el video por streaming en paquetes, sin almacenar el video completo localmente.
- **FR-003**: La duración de referencia del clip es de 10 minutos, pero la grabación continua puede durar más.
- **FR-004**: La app MUST enviar al modelo remoto la duración del clip y un ID único por solicitud.
- **FR-005**: El modelo remoto MUST devolver la traducción en texto en tiempo real.
- **FR-006**: La app MUST mostrar las traducciones en un chat con historial de hasta las últimas 30 traducciones.
- **FR-007**: La app MUST generar audio a partir del texto mediante TTS con los permisos necesarios.
- **FR-008**: La app MUST funcionar con baja conexión.
- **FR-009**: La app MUST NOT requerir inicio de sesión ni guardar datos en la nube.
- **FR-010**: La app MUST manejar errores de forma clara para evitar confusiones.

### Key Entities *(include if feature involves data)*

- **Traducción**: texto resultante, timestamp, id único.
- **Clip**: sección de video organizable con timestamp obtenido por el servidor para procesarlo.
- **Chat**: historial de hasta 30 traducciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El usuario recibe la traducción en texto en menos de 5 segundos tras enviar un clip típico.
- **SC-002**: El historial conserva correctamente las últimas 30 traducciones.
- **SC-003**: La app funciona con conexión de baja calidad sin pérdida de datos.
- **SC-004**: El 90% de los usuarios completa el flujo principal en el primer intento.

## Assumptions

- El usuario otorga permisos de cámara y audio.
- El modelo remoto está disponible y responde en tiempo real.
- La conexión, aunque baja, permite streaming por paquetes.
- No se almacenan datos en la nube ni se requiere autenticación.