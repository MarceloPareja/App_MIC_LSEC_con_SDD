# Feature Specification: Traductor de Lengua de Señas Ecuatoriana (TraductorLSEC)

**Feature Branch**: `feature/RetrabajoGemini`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "La app móvil "TraductorLSEC" permitirá que una persona que no conoce lengua de señas ecuatoriana (LSEC) pueda comprender a una persona sorda que si la conozca, al enviar un video de las señas con máximo de 10 min en un streaming del video constante por paquetes para no consumir espacio del dispositivo innecesario. La aplicación debe tener acceso completo a la cámara para esta función. El video será procesado por un modelo de deep learning externo desplegado en la nube que necesitara la duración del clip enviado para el procesamiento e id unico, que devolverá en tiempo real la traducción de las señas en forma de texto en un chat con historial hasta 30 ultimas traducciones en un chat tipo respuesta whatsapp y un tts ayudara en el cliente movil generar el audio audio con los permisos para esto. La aplicación debe ser altamente intuitiva y fácil de usar; el manejo de errores es clave para evitar confusiones o malentendidos por parte del usuario. Debe tener la capacidad de trabajar con baja conexión. La app no necesita de un inicio de sesión ya que no guarda datos en la nube, solo usa el modelo remoto para procesar"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Streaming de video de señas y traducción en tiempo real (Priority: P1)

Como una persona oyente que no conoce LSEC, quiero utilizar la cámara de mi dispositivo móvil para transmitir en streaming por paquetes (de hasta 10 minutos) las señas de una persona sorda, enviando un ID único y la duración al modelo remoto en la nube, para recibir en tiempo real la traducción en texto en un chat con historial de hasta 30 mensajes y generar audio mediante TTS, sin necesidad de iniciar sesión.

**Why this priority**: Es el núcleo funcional de la aplicación (traducción de LSEC en tiempo real mediante streaming de video y TTS).

**Independent Test**: Se puede probar completamente simulando el envío de paquetes de video desde la cámara, validando la comunicación con el modelo remoto, la recepción de texto traducido en el chat y la generación de audio por TTS.

**Acceptance Scenarios**:
1. **Given** que la aplicación está abierta sin requerir inicio de sesión y con permisos de cámara concedidos, **When** el usuario inicia la captura y streaming por paquetes de un video de señas, **Then** el sistema transmite los paquetes indicando la duración y el ID único al modelo en la nube.
2. **Given** que el modelo remoto procesa el video, **When** la traducción es devuelta, **Then** aparece en tiempo real en la interfaz de chat tipo WhatsApp y se genera el audio correspondiente mediante TTS.
3. **Given** que el chat contiene múltiples traducciones, **When** el número de mensajes supera 30, **Then** el historial se mantiene limitado estrictamente a las últimas 30 traducciones.

---

### User Story 2 - Manejo de errores y baja conectividad (Priority: P2)

Como usuario de la aplicación en entornos con conectividad limitada, quiero que el sistema maneje los errores de red y baja conexión de manera intuitiva y amigable, evitando confusiones o malentendidos.

**Why this priority**: Garantiza la usabilidad y resiliencia de la app en condiciones reales de baja conectividad.

**Independent Test**: Se puede probar simulando cortes de red o conexión lenta durante el streaming de video y verificando que los mensajes de error sean claros y comprensibles.

**Acceptance Scenarios**:
1. **Given** que el dispositivo experimenta baja conexión o pérdida de red, **When** el streaming de video intenta enviar paquetes, **Then** la aplicación muestra notificaciones claras de estado y reintenta o pausa la transmisión sin bloquear la interfaz.
2. **Given** que ocurre un error de procesamiento o permisos, **When** el sistema lo detecta, **Then** presenta mensajes intuitivos al usuario que previenen malentendidos.

---

### Edge Cases

- ¿Qué sucede si el video excede el límite de 10 minutos de streaming continuo? El sistema notifica al usuario y reinicia o segmenta la sesión de streaming.
- ¿Cómo se comporta la app si se deniegan los permisos de cámara o audio (TTS)? Se muestra una guía visual explicando la necesidad de los permisos para operar.
- ¿Qué ocurre ante una desconexión total de red? Se almacena temporalmente el estado local del chat y se notifica al usuario de la pérdida temporal de conectividad con el modelo remoto.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La aplicación MUST permitir el acceso completo a la cámara del dispositivo móvil para la captura de video de LSEC.
- **FR-002**: La aplicación MUST transmitir el video en streaming constante por paquetes (con un límite máximo de 10 minutos por clip) para optimizar el almacenamiento del dispositivo.
- **FR-003**: La aplicación MUST enviar cada paquete de video junto con la duración del clip y un identificador único (ID único) al modelo de deep learning externo en la nube.
- **FR-004**: La aplicación MUST recibir en tiempo real la traducción de las señas en forma de texto y mostrarla en una interfaz de chat tipo respuesta de WhatsApp.
- **FR-005**: La aplicación MUST mantener un historial de chat limitado estrictamente a las últimas 30 traducciones realizadas.
- **FR-006**: La aplicación MUST generar audio en el cliente móvil a partir del texto traducido utilizando Text-to-Speech (TTS), requiriendo los permisos de audio correspondientes.
- **FR-007**: La aplicación MUST operar con capacidad de trabajo ante baja conexión a internet, notificando adecuadamente el estado de red.
- **FR-008**: La aplicación MUST proporcionar un manejo de errores altamente intuitivo y fácil de usar para evitar confusiones o malentendidos en el usuario.
- **FR-009**: La aplicación MUST operar sin requerir inicio de sesión ni almacenamiento de datos personales en la nube, utilizando el modelo remoto exclusivamente para el procesamiento de traducción.

### Key Entities

- **Sesión de Streaming de Video**: Representa el flujo de paquetes de video de hasta 10 minutos capturados por la cámara, caracterizado por un ID único y la duración del clip.
- **Mensaje de Traducción**: Representa una traducción de señas a texto, conteniendo el texto traducido, marca de tiempo y estado de reproducción de audio por TTS.
- **Historial de Chat**: Colección local en el dispositivo que almacena hasta las últimas 30 traducciones en formato de chat interactivo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 95% de las sesiones de streaming de video por paquetes se completan sin saturar ni consumir espacio innecesario en el almacenamiento local del dispositivo.
- **SC-002**: Las traducciones en texto se muestran en la interfaz de chat en tiempo real con una latencia perceptible menor a 2 segundos bajo conexión estándar.
- **SC-003**: El historial del chat mantiene de forma estricta un límite máximo de 30 traducciones, eliminando las más antiguas de manera automática.
- **SC-004**: El cliente móvil genera exitosamente el audio mediante TTS en el 100% de las traducciones donde el usuario active la reproducción o síntesis automática.
- **SC-005**: El manejo de errores y notificaciones de baja conectividad son considerados claros e intuitivos en las pruebas de usabilidad con usuarios.
- **SC-006**: La aplicación opera de forma totalmente autónoma sin requerir inicio de sesión en ningún momento del flujo de uso.

## Assumptions

- El modelo de deep learning en la nube está operativo y expone un endpoint que acepta ID único y duración del clip junto con los paquetes de video.
- El sistema operativo móvil otorga los permisos necesarios de cámara y síntesis de voz (TTS) al ser solicitados.
- La baja conexión se maneja mediante mecanismos estándar de reintento y notificación de red en el cliente móvil.
