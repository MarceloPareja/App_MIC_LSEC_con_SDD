# Feature Specification: TraductorLSEC

**Feature Branch**: `001-traductor-lsec`  
**Created**: 2026-10-20  
**Status**: Draft  
**Input**: User description: La app móvil  "TraductorLSEC" permitirá que una persona que no conoce lengua de señas ecuatoriana (LSEC) pueda comprender a una persona sorda que si la conozca, al enviar un video de las señas con máximo de 10 min en un streaming del video constante por paquetes para no consumir espacio del dispositivo innecesario. La aplicación debe tener acceso completo a la cámara para esta función. El video será procesado por un modelo de deep learning externo desplegado en la nube que necesitara la duración del clip enviado para el procesamiento e id unico, que devolverá en tiempo real la traducción de las señas en forma de texto en un chat con historial hasta 30 ultimas traducciones en un chat tipo respuesta whatsapp y un tts ayudara en el cliente movil generar el audio audio con los permisos para esto. La aplicación debe ser altamente intuitiva y fácil de usar; el manejo de errores es clave para evitar confusiones o malentendidos por parte del usuario. Debe tener la capacidad de trabajar con baja conexión. La app no necesita de un inicio de sesión ya que no guarda datos en la nube, solo usa el modelo remoto para procesar.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real-time sign translation (Priority: P1)

A hearing person who does not know Ecuadorian Sign Language (LSEC) wants to understand a deaf person who does know LSEC. They open the app, grant camera access, and record/stream signs for up to 10 minutes; the app sends video in constant packets (streaming) without storing large files unnecessarily, receives real-time text translation from the remote model, sees it in a WhatsApp-style chat, and can have it read aloud via TTS.

**Why this priority**: Core value proposition - enables communication between hearing and deaf users in real time.

**Independent Test**: Can be tested by streaming a short LSEC clip (e.g., greeting) and verifying text appears in chat with TTS available.

**Acceptance Scenarios**:

1. **Given** camera permission granted and network available, **When** user starts streaming signs, **Then** video is sent in packets (no full local large file required) and translation text appears in chat in near real-time.
2. **Given** translation text received, **When** user requests audio, **Then** TTS generates and plays audio on the device (with required permissions).
3. **Given** user streams up to 10 minutes, **When** streaming completes or stops, **Then** session handling does not require unnecessary local storage of the full clip.

---

### User Story 2 - Low connectivity resilience (Priority: P2)

User is in an area with low/unstable connection. The app remains usable with clear error messages and graceful degradation without confusing the user.

**Why this priority**: Must work with low connection as specified.

**Independent Test**: Simulate network drops/retries and verify error messages are clear and user can recover or retry.

**Acceptance Scenarios**:

1. **Given** low/unstable connection, **When** packets fail to send/receive, **Then** app shows clear, non-technical error guidance and allows retry without crashing.
2. **Given** connection drops mid-stream, **When** user attempts to resume, **Then** app handles gracefully with appropriate messaging.

---

### User Story 3 - Intuitive chat history (Priority: P3)

User wants to review recent translations. The app shows translations in a WhatsApp-style chat with history limited to the last 30 translations.

**Why this priority**: Provides context without persisting data to cloud long-term.

**Independent Test**: Perform several translations and verify only last 30 appear; older ones are not retained beyond that limit.

**Acceptance Scenarios**:

1. **Given** more than 30 translations occur, **When** viewing chat, **Then** only the most recent 30 translations are shown.
2. **Given** no login/session, **When** app is used, **Then** no cloud storage of user data occurs; history is local to session/device context as specified.

---

### Edge Cases

- What happens when camera permission is denied? App must show clear guidance to grant access.
- What happens if video exceeds 10 minutes? App must enforce or clearly communicate the 10-minute limit.
- What happens if remote model is unreachable? Clear error handling with retry guidance.
- What happens if TTS not available/permissions denied? App must handle gracefully without breaking translation flow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: App MUST require and use full camera access for the sign capture/streaming function.
- **FR-002**: App MUST stream video in constant packets (not require storing the full video file unnecessarily on the device) for clips up to 10 minutes.
- **FR-003**: App MUST send to the external cloud deep learning model: the duration of the clip sent and a unique ID for the request/stream.
- **FR-004**: The remote model MUST return translation of signs as text in real-time.
- **FR-005**: App MUST display translations in a WhatsApp-style chat with history limited to the last 30 translations.
- **FR-006**: App MUST use TTS on the mobile client to generate audio from translated text, with appropriate permissions.
- **FR-007**: App MUST be highly intuitive and easy to use.
- **FR-008**: App MUST have robust error handling to avoid confusion/misunderstandings.
- **FR-009**: App MUST be capable of working with low connection.
- **FR-010**: App MUST NOT require user login; it MUST NOT store data in the cloud (only uses remote model for processing).

### Key Entities *(include if feature involves data)*

- **Translation**: Text result from remote model, associated with a request/unique ID and timestamp; part of chat history (max 30).
- **Stream Session**: Ongoing streaming session with duration tracking, unique ID, packet stream to remote model.
- **Chat Message**: Representation in WhatsApp-style chat (translation + optional audio availability).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can start translation within 10 seconds of granting camera access.
- **SC-002**: For clips under 10 minutes, video is streamed in packets with no unnecessary full-file storage on device (verified by design requirement).
- **SC-003**: Translations appear in chat in near real-time under normal network conditions.
- **SC-004**: Chat history never exceeds 30 most recent translations.
- **SC-005**: App functions (with appropriate messaging) under low connection scenarios without crashing.
- **SC-006**: No user login required and no cloud storage of user data occurs.
- **SC-007**: TTS audio can be generated from translations when permissions granted.
- **SC-008**: Error messages are clear and actionable to prevent confusion.

## Assumptions

- Remote deep learning model is deployed in the cloud and accessible over network.
- Device has camera and supports TTS; permissions will be requested as needed.
- "Streaming in constant packets" means chunked transmission during capture without writing large temporary files.
- Unique ID is generated per stream/session for the remote model.
- Duration of clip sent is provided to the remote model for processing.

## Out of Scope

- User accounts/authentication
- Cloud storage of user data/history
- Offline translation (model is external/remote)
- Support for other sign languages beyond LSEC
- Long-term history beyond last 30 translations
