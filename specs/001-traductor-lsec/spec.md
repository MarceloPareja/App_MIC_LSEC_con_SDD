# Feature Specification: Aplicación Móvil TraductorLSEC

**Feature Branch**: `feature/traductor-lsec`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "Crea la app móvil "TraductorLSEC" que permitirá que una persona que no conoce lengua de señas ecuatoriana (LSEC) pueda comprender a una persona sorda que si la conozca, al enviar un video de la seña que puede ser una grabación o puede ser un video grabado en vivo con máximo de 10 min. La aplicación tendrá acceso completo a la cámara para esta función. El video será procesado por un modelo de deep learning externo desplegado en la nube que devolverá en tiempo real la traducción de las señas en forma de texto y audio. La aplicación debe ser altamente intuitiva y fácil de usar. Debe tener la capacidad de trabajar con baja conexión. La app no necesita de un inicio de sesión ya que no guarda datos en la nube, solo usa el modelo remoto para procesar."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Traducción en Tiempo Real de Video en Vivo (Priority: P1)

Una persona oyente que no conoce Lengua de Señas Ecuatoriana (LSEC) abre la aplicación móvil TraductorLSEC sin necesidad de registrarse y utiliza la cámara del dispositivo para grabar en vivo a una persona sorda gesticulando en LSEC (hasta 10 minutos). El sistema transmite o procesa el video a través del modelo de deep learning en la nube y presenta instantáneamente la traducción en formato de texto legible y síntesis de voz (audio).

**Why this priority**: Es la funcionalidad central y el caso de uso principal que resuelve la necesidad de comunicación directa e inmediata entre personas oyentes y sordas.

**Independent Test**: Se puede probar abriendo la cámara en modo grabación en vivo, simulando o capturando un video de señas de hasta 10 minutos, y verificando que el sistema muestre el texto traducido y emita la reproducción de audio correspondiente.

**Acceptance Scenarios**:

1. **Given** que la aplicación móvil está abierta y sin sesión iniciada, **When** el usuario selecciona la opción de grabación de video en vivo y concede acceso a la cámara, **Then** la cámara inicia la captura de video de hasta 10 minutos con indicadores visuales claros de grabación.
2. **Given** que se está grabando un video en vivo de una seña en LSEC, **When** el video es procesado por el servicio en la nube, **Then** la aplicación muestra en tiempo real la traducción en texto y reproduce el resultado en audio con claridad.

---

### User Story 2 - Envío de Video Grabado Previamente (Priority: P2)

Una persona oyente selecciona un archivo de video existente de hasta 10 minutos desde la galería de su dispositivo móvil y lo envía a través de la aplicación TraductorLSEC para obtener su traducción automática a LSEC sin requerir autenticación.

**Why this priority**: Permite procesar videos previamente almacenados, ofreciendo flexibilidad cuando no se realiza una interacción cara a cara en tiempo real.

**Independent Test**: Se puede probar seleccionando un video guardado en el dispositivo y enviándolo al sistema, comprobando que se procese correctamente y devuelva el texto y audio traducidos.

**Acceptance Scenarios**:

1. **Given** que la aplicación está en la pantalla principal de selección, **When** el usuario selecciona un video grabado previamente de la galería (con duración máxima de 10 minutos), **Then** el sistema carga y envía el video al modelo remoto para su procesamiento.
2. **Given** que un video grabado ha sido procesado, **When** el servidor devuelve los resultados, **Then** la aplicación presenta la traducción en texto y audio de forma intuitiva.

---

### User Story 3 - Operación con Baja Conexión y Resiliencia (Priority: P3)

El usuario utiliza la aplicación en entornos con conectividad de red limitada o intermitente, y el sistema gestiona la cola de envío, reintentos y almacenamiento temporal local de manera transparente hasta completar la traducción.

**Why this priority**: Garantiza la usabilidad en condiciones reales de conectividad variable en Ecuador.

**Independent Test**: Se puede probar simulando una red lenta o desconexión temporal durante el envío del video, verificando que la aplicación notifique el estado de sincronización y reintente el procesamiento al restablecerse la señal.

**Acceptance Scenarios**:

1. **Given** que el dispositivo presenta baja conexión a internet al enviar un video, **When** se intenta realizar la traducción, **Then** la aplicación notifica el estado de red y reintenta la transmisión de forma automática y controlada.
2. **Given** que la conexión se restablece tras una intermitencia, **When** el video pendiente es procesado con éxito, **Then** se muestran el texto y el audio traducidos al usuario.

### Edge Cases

- ¿Qué sucede cuando el video grabado en vivo o seleccionado supera los 10 minutos de duración? El sistema muestra una alerta clara indicando el límite máximo permitido y permite recortar o seleccionar un fragmento válido.
- ¿Qué sucede si el usuario deniega el permiso de acceso a la cámara o almacenamiento? La aplicación muestra una guía accesible explicando la necesidad del permiso y ofreciendo un acceso directo a la configuración del dispositivo.
- ¿Qué ocurre ante una pérdida total de conexión durante la transmisión del video? La aplicación almacena temporalmente la solicitud y ofrece la opción de reintentar manualmente o en segundo plano cuando la señal mejore.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La aplicación móvil DEBE proporcionar acceso directo e intuitivo a la cámara del dispositivo para la grabación de video en vivo de hasta 10 minutos.
- **FR-002**: La aplicación móvil DEBE permitir la selección y envío de videos grabados previamente desde la galería del dispositivo con una duración máxima de 10 minutos.
- **FR-003**: El sistema DEBE integrar el procesamiento del video mediante un modelo de deep learning externo desplegado en la nube.
- **FR-004**: La aplicación DEBE mostrar la traducción obtenida en formato de texto legible en tiempo real.
- **FR-005**: La aplicación DEBE reproducir la traducción en formato de audio (síntesis de voz) de forma clara y sincronizada.
- **FR-006**: La aplicación DEBE operar sin necesidad de registro ni inicio de sesión (usuario anónimo), garantizando que no se almacenen datos personales o sensibles en la nube.
- **FR-007**: La aplicación DEBE incorporar mecanismos de manejo de baja conexión, incluyendo reintentos automáticos y notificaciones de estado de red al usuario.
- **FR-008**: La interfaz de usuario DEBE ser altamente intuitiva, accesible y fácil de usar, cumpliendo con principios de diseño móvil centrado en el usuario.

### Success Criteria

- **SC-001**: El 95% de los usuarios completan con éxito el proceso de traducción (desde la grabación/selección hasta la obtención de texto y audio) en menos de 2 minutos por video de prueba.
- **SC-002**: La latencia percibida por el usuario desde el envío del video hasta la recepción de la traducción en texto y audio es inferior a 5 segundos bajo condiciones de conectividad estándar.
- **SC-003**: La aplicación opera correctamente y gestiona escenarios de baja conectividad con una tasa de éxito en reintentos de al menos el 90%.
- **SC-004**: La interfaz obtiene una puntuación de usabilidad superior al 90% en pruebas de satisfacción con usuarios no familiarizados con LSEC.
- **SC-005**: 100 de cada 100 ejecuciones de compilación y pruebas automatizadas se completan sin errores previos a la integración.
