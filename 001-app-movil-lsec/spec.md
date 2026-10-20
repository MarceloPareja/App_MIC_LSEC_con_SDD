# Feature Specification: App móvil cliente para la traducción de LSEC

**Feature Branch**: `001-app-movil-lsec`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "App móvil cliente para la traducción de Lengua de Señas Ecuatoriana (LSEC) mediante inferencia en la nube, con entrega del resultado en texto y voz. Alcance limitado a la aplicación móvil cliente; el servicio de inferencia en la nube se asume disponible y fuera de alcance."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obtener la traducción en texto de una seña (Priority: P1)

Una persona sorda, durante una conversación presencial, activa la captura desde la
aplicación, muestra su seña ante la cámara durante unos segundos y obtiene en pantalla el
texto que representa lo que quiso expresar. La persona puede leer el mensaje y responder a
su interlocutor oyente sin intermediario.

**Why this priority**: Sin la traducción en texto no hay valor de uso alguno; es el
resultado mínimo que hace que la aplicación resuelva el problema que la motivó. Cualquier
otra capacidad (voz, historial) solo amplía un resultado que debe existir primero.

**Independent Test**: Se puede verificar de forma autónoma con una muestra de seña
grabada y un servicio de inferencia disponible: al capturar y enviar la muestra, la
persona usuaria obtiene un texto en pantalla sin necesitar ninguna otra funcionalidad
habilitada.

**Acceptance Scenarios**:

1. **Given** la aplicación abierta y la persona usuaria con permisos de cámara y micrófono
   concedidos, **When** inicia una captura y mantiene la seña ante la cámara, **Then** la
   aplicación captura la muestra y la envía al servicio de inferencia.
2. **Given** una muestra enviada y el servicio procesándola, **When** el servicio devuelve
   la traducción, **Then** la aplicación muestra el texto traducido en pantalla de forma
   legible, con tamaño de letra y contraste adecuados para lectura sostenida.
3. **Given** una traducción ya mostrada, **When** la persona usuaria cierra la sesión,
   **Then** la traducción queda registrada en el historial y puede volver a consultarse.
4. **Given** la aplicación abierta, **When** la persona usuaria cancela la captura antes de
   enviarla, **Then** la muestra se descarta, no se envía nada al servicio y la aplicación
   vuelve al estado inicial.

---

### User Story 2 - Escuchar la traducción en voz (Priority: P2)

La persona sorda, además de leer la traducción, puede escucharla en voz alta para
compartirla con su interlocutor oyente o para sostener una conversación en un entorno con
ruido donde leer no es cómodo. Puede silenciar la voz cuando necesita hablar ella misma.

**Why this priority**: La entrega por voz fue confirmada como parte del resultado esperado
y es lo que permite el uso conversacional bidireccional, pero el texto ya cubre el
resultado esencial, por eso queda en segundo lugar.

**Independent Test**: Se puede verificar de forma autónoma tomadas las traducciones
producidas por el flujo de texto: la persona usuaria activa la reproducción por voz y
escucha la lectura del texto, sin requerir historial ni otras funciones.

**Acceptance Scenarios**:

1. **Given** una traducción visible en pantalla, **When** la persona usuaria activa la
   reproducción por voz, **Then** la aplicación lee en voz alta el texto traducido.
2. **Given** la reproducción por voz en curso, **When** la persona usuaria la detiene o
   silencia el dispositivo, **Then** la lectura se interrumpe de inmediato y el texto
   permanece visible.
3. **Given** una traducción ya reproducida, **When** la persona usuaria vuelve a abrirla
   desde el historial, **Then** puede escucharla de nuevo sin volver a capturarla.

---

### User Story 3 - Revisar traducciones anteriores (Priority: P3)

La persona usuaria consulta un listado de las traducciones más recientes para releer un
mensaje que no alcanzó a ver, confirmar un dato o reproducirlo en voz, incluso cuando en
ese momento no tiene conexión.

**Why this priority**: Aporta control y evita repetir capturas, pero no bloquea la
traducción en el momento de la conversación, que es el uso principal.

**Independent Test**: Se puede verificar de forma autónoma con traducciones ya generadas:
el historial las lista, permite abrir su detalle y reproducirlas sin conexión.

**Acceptance Scenarios**:

1. **Given** traducciones generadas en sesiones anteriores, **When** la persona usuaria
   abre el historial, **Then** ve sus traducciones más recientes ordenadas de la más
   reciente a la más antigua.
2. **Given** un historial existente, **When** la persona usuaria abre el dispositivo sin
   conexión, **Then** las traducciones guardadas siguen siendo consultables y su texto se
   puede leer y reproducir.
3. **Given** un historial con muchas entradas, **When** la persona usuaria busca una
   traducción concreta, **Then** puede localizarla por texto y por fecha.

---

### User Story 4 - Comprender y recuperar un fallo de forma clara (Priority: P4)

Cuando el servicio de inferencia no responde, la conexión se cae o la seña capturada no es
interpretable, la persona usuaria recibe un mensaje comprensible que explica qué ocurrió y
qué puede hacer, sin quedarse mirando una pantalla en blanco ni perder la muestra ya
capturada.

**Why this priority**: La confianza en la herramienta depende de que los fallos se
comuniquen bien, pero solo tiene efecto cuando existe un camino feliz funcionando.

**Independent Test**: Se puede verificar de forma autónoma simulando condiciones de fallo
del servicio: la aplicación muestra un mensaje accionable y permite reintentar sin
repetir la captura.

**Acceptance Scenarios**:

1. **Given** una muestra enviada, **When** el servicio no responde dentro del tiempo
   esperado, **Then** la aplicación informa que no pudo completar la traducción, explica
   la causa de forma comprensible y ofrece reintentar.
2. **Given** una traducción con nivel de confianza bajo, **When** el resultado se muestra,
   **Then** la aplicación lo señala como poco fiable en lugar de presentarlo como una
   traducción segura.
3. **Given** una captura en curso, **When** se pierde la conexión, **Then** la aplicación
   conserva la muestra capturada y permite reenviarla cuando vuelva la conexión.
4. **Given** que faltan los permisos de cámara o micrófono, **When** la persona usuaria
   intenta capturar, **Then** la aplicación explica qué permiso falta y cómo otorgarlo.

---

### Edge Cases

- **Qué ocurre cuando la seña capturada es ambigua o no corresponde a una seña
  reconocible**: el resultado se devuelve con confianza baja o sin resultado válido; la
  aplicación lo comunica y ofrece repetir la captura, sin inventar una traducción.
- **Cómo maneja el sistema un resultado en un idioma distinto al esperado**: la aplicación
  lo muestra indicando el idioma detectado en lugar de asumir que es incorrecto.
- **Qué sucede si la persona usuaria captura una muestra demasiado corta o demasiado
  larga**: la aplicación indica que la captura no cumple el mínimo o el máximo admisible y
  guía para repetirla.
- **Cómo se comporta la aplicación si la persona usuaria la pone en segundo plano durante
  la captura**: la captura se cancela de forma segura y la persona vuelve a un estado
  consistente al volver a la aplicación.
- **Cómo se comporta la aplicación si el volumen del dispositivo está en silencio o la
  reproducción por voz no está disponible**: la persona usuaria recibe una indicación
  clara y puede seguir usando el texto.
- **Qué ocurre con las traducciones muy extensas**: el texto se muestra completo, sin
  truncarse silenciosamente, y la reproducción por voz recorre el texto completo.
- **Cómo se manejan las traducciones guardadas cuando la persona usuaria borra su
  historial**: las entradas se eliminan de forma definitiva y verificable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La aplicación MUST ofrecer una acción única y visible para iniciar una
  captura de la seña desde la pantalla principal.
- **FR-002**: La aplicación MUST capturar una muestra de la seña y enviarla al servicio de
  inferencia para su procesamiento.
- **FR-003**: La aplicación MUST mostrar de forma visible el estado del proceso de
  traducción (inicio, envío, análisis, resultado o fallo) en todo momento.
- **FR-004**: La aplicación MUST mostrar el texto de la traducción en pantalla cuando el
  servicio devuelve un resultado válido.
- **FR-005**: La aplicación MUST ofrecer la reproducción en voz del texto traducido y MUST
  permitir detenerla o silenciarla de inmediato.
- **FR-006**: La aplicación MUST permitir repetir la reproducción en voz de una traducción
  ya obtenida sin requerir una nueva captura.
- **FR-007**: La aplicación MUST conservar las traducciones más recientes en el
  dispositivo y MUST permitir consultarlas ordenadas de la más reciente a la más antigua.
- **FR-008**: La aplicación MUST permitir localizar una traducción guardada por su texto y
  por su fecha.
- **FR-009**: La aplicación MUST permitir consultar y reproducir las traducciones
  guardadas cuando el dispositivo no tiene conexión.
- **FR-010**: La aplicación MUST informar de forma comprensible cuando el servicio de
  inferencia no está disponible o no responde dentro del tiempo esperado, y MUST ofrecer
  una acción de reintento.
- **FR-011**: La aplicación MUST reintentar la traducción con la muestra ya capturada
  cuando la causa del fallo sea recuperable, sin exigir una nueva captura.
- **FR-012**: La aplicación MUST señalar de forma explícita cuando el resultado tiene
  confianza baja, en lugar de presentarlo como una traducción fiable.
- **FR-013**: La aplicación MUST indicar el idioma del resultado cuando este difiera del
  idioma de salida configurado.
- **FR-014**: La aplicación MUST validar la disponibilidad de los permisos de cámara y
  micrófono antes de capturar y MUST explicar cómo otorgarlos cuando falten.
- **FR-015**: La aplicación MUST informar cuando la captura no cumple la duración mínima o
  máxima admisible y MUST guiar para repetirla.
- **FR-016**: La aplicación MUST descartar la captura si la persona usuaria cancela antes
  del envío y MUST NOT enviar la muestra al servicio en ese caso.
- **FR-017**: La aplicación MUST NOT conservar la muestra audiovisual de la seña una vez
  procesada; solo MUST conservar el texto de la traducción y sus metadatos.
- **FR-018**: La aplicación MUST NOT enviar al servicio información que identifique a la
  persona usuaria y MUST NOT mostrar datos personales en la interfaz.
- **FR-019**: La aplicación MUST mantener el texto de la traducción visible y legible
  mientras la persona usuaria consulta el historial o reproduce la voz.
- **FR-020**: La aplicación MUST permitir a la persona usuaria borrar su historial de
  traducciones de forma definitiva y verificable.

### Key Entities *(include if feature involves data)*

- **Muestra de seña**: captura audiovisual de la seña realizada por la persona usuaria,
  con su duración y momento de captura. Existe únicamente mientras se procesa.
- **Traducción**: texto traducido con su idioma de origen y destino, su nivel de
  confianza, su fecha y hora de generación y su estado de reproducción. Es la unidad que la
  aplicación muestra, conserva y reproduce.
- **Historial de traducciones**: conjunto ordenado de las traducciones guardadas en el
  dispositivo, consultable por texto y por fecha y descartable por la persona usuaria.
- **Preferencias de reproducción**: ajustes de reproducción de la voz, por ejemplo la
  activación o desactivación de la lectura automática y el control del volumen.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Al menos el 90 % de las personas usuarias de prueba obtiene el texto de la
  traducción en menos de 10 segundos desde el inicio de la captura, con servicio
  disponible y seña de calidad suficiente.
- **SC-002**: Al menos el 95 % de las capturas de señas claras y bien encuadradas
  producen un texto de traducción visible en pantalla.
- **SC-003**: La reproducción por voz comienza en menos de 1 segundo desde que la
  traducción está disponible en pantalla.
- **SC-004**: Al menos el 90 % de las personas usuarias de prueba completa la tarea
  "traducir una seña y obtener texto y voz" sin ayuda externa en su primer intento.
- **SC-005**: En el 100 % de los escenarios de fallo controlados, la persona usuaria ve un
  mensaje comprensible y dispone de una acción de reintento; nunca se presenta un fallo
  silencioso.
- **SC-006**: El 100 % de las traducciones guardadas siguen siendo consultables y
  reproducibles durante las 24 horas posteriores a su generación, con el dispositivo sin
  conexión.
- **SC-007**: El 100 % de los resultados con confianza baja se señalan en la interfaz como
  poco fiables; ninguno se presenta como una traducción segura.

## Assumptions

- El servicio de inferencia en la nube existe, es estable y cumple un contrato que recibe
  una muestra audiovisual de la seña y devuelve el texto traducido con su nivel de
  confianza. Su diseño, implementación y despliegue quedan fuera de esta feature.
- La muestra enviada es un clip de video corto que incluye la pista de audio de la voz.
- Los idiomas de la v1 son: seña de entrada LSEC y salida en español. La elección de otros
  idiomas de destino queda fuera de esta feature.
- La aplicación se usa en conversación presencial, con el dispositivo en la mano y con
  conectividad a internet disponible la mayor parte del tiempo; la operación sin conexión
  cubre únicamente el historial ya generado.
- Los permisos de cámara y micrófono son otorgables por la persona usuaria desde los
  ajustes del dispositivo, y la aplicación puede detectarlos y explicarlos.
- La legibilidad de la interfaz (tamaño de letra y contraste) se valida con personas sordas
  durante la verificación; la v1 debe permitir ampliar el tamaño del texto.
- Fuera de alcance en esta feature: el modelo de inferencia y su despliegue, el servicio de
  inferencia y su interfaz de programación, el panel web de administración, los subtítulos
  en vivo sobre el video, el reconocimiento de vocabulario técnico, las cuentas de usuario
  en la nube y la persistencia de las muestras de seña en el dispositivo.
- La cantidad máxima de traducciones conservadas en el historial y la duración máxima de
  cada captura se fijan durante la planificación, con valores por defecto razonables que
  la persona usuaria no tiene que configurar.
