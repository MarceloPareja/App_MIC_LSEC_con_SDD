# Research: App móvil cliente para la traducción de LSEC

**Feature**: 001-app-movil-lsec | **Fecha**: 2026-10-20 | **Fase**: 0 (Outline & Research)

Este documento consolida las decisiones técnicas tomadas para la fase de diseño. Cada
decisión sigue el formato *Decision / Rationale / Alternatives considered*. Los artefactos
derivados son `plan.md`, `data-model.md`, `contracts/inference-api.md` y `quickstart.md`.

**Alcance de la investigación**: la app móvil cliente. El servicio de inferencia en la nube
es una feature separada y no existe todavía; el cliente se define contra un contrato
documentado y se desarrolla contra un servidor simulado.

---

## D-1. Stack de implementación del cliente

**Decision**: Flutter (Dart 3.x) como base de código única para Android e iOS, dentro de
`mobile/`. Bibliotecas: `camera` (grabación con audio), `flutter_tts` (síntesis de voz del
sistema), `dio` (HTTP con streaming, timeouts y reintentos), `drift` + `drift_flutter`
(persistencia local en SQLite), `path_provider` (rutas de caché), `mocktail` (dobles de
prueba). Pruebas con `flutter_test` (unitarias y de widgets) e `integration_test`.

**Rationale**: El equipo es de una sola persona, así que la productividad manda: Flutter
permite iterar sobre la interfaz (que es el grueso de los FR) con un solo código para
Android e iOS, y expone todas las capacidades exigidas por la especificación: captura de
video con audio, TTS del sistema en español, SQLite local y semántica de accesibilidad.
`drift` aporta consultas tipadas y migraciones, que es lo que necesitan el historial y su
búsqueda. `dio` resuelve en una sola dependencia el streaming de la subida, los timeouts y
la política de reintentos que exige SC-001.

**Alternatives considered**:
- *Android nativo (Kotlin + Compose)*: mejor control nativo de la voz en español y de
  TalkBack, pero obliga a un segundo cliente para iOS y duplica el trabajo de UI para un
  equipo de una persona.
- *React Native*: reutiliza JavaScript, pero añade una superficie de módulos nativos que
  alguien debe mantener (cámara, TTS) y una capa de puente que resta valor a la
  simplicidad.
- *iOS nativo (Swift)*: no cubre Android, que es la plataforma mayoritaria del mercado
  objetivo en Ecuador, y exige macOS para compilar.

**Riesgos asumidos**: churn de versiones de plugins ( mitigated con versiones fijadas en
`pubspec.yaml`), y dependencia de la disponibilidad de la voz española en el dispositivo
(ver D-5).

---

## D-2. Mecanismo de subida de la muestra

**Decision**: `POST /v1/translate` con `multipart/form-data`: una parte `metadata` en JSON
y una parte `file` con los bytes MP4. Se descarta la opción de URL prefirmada en la v1.

**Rationale**: Un único viaje de ida y vuelta pone el video en marcha de inmediato, que es
la restricción que impone SC-001 (texto en pantalla en menos de 10 s). Base64 inflaría el
cuerpo un 33 % (20 MB → 26,7 MB) y obligaría a materializar el archivo completo en
memoria, en un dispositivo de gama media. La URL prefirmada añadiría 2-3 viajes extra,
una caducidad de 15 minutos y una máquina de estados que debe sobrevivir al primer plano
de la aplicación. El streaming desde la caché privada permite además mostrar progreso real
en bytes para el estado "enviando" (FR-003).

**Alternatives considered**:
- *base64 en JSON*: +33 % de datos móviles, dos copias completas en memoria, rompe la
  compresión HTTP y hace peligroso registrar el cuerpo.
- *URL prefirmada de almacenamiento de objetos*: se descarta para la v1; se reevalúa si los
  clips superan ~50 MB o se necesita subida reanudable.

---

## D-3. Restricciones de la muestra y calidad de captura

**Decision**: el cliente captura y valida antes de enviar: duración entre 1,5 s y 10 s,
tamaño máximo 25 MB, contenedor MP4 (H.264 + AAC-LC), audio mono a 48 kHz, y una tasa de
bits objetivo que deje el clip entre 0,5 y 3 MB.

**Rationale**: Un clip de 20 MB no se sube ni se procesa en 10 s sobre una conexión de
3 Mbps (20 MB ≈ 53 s solo de subida). El servicio no puede corregirlo: **la calidad de
captura la fija el cliente**. Además, el 10 s de duración máxima coincide con el máximo que
acepta el servicio, de modo que capturar más allá solo genera rechazos.

**Alternatives considered**: *dejar que el servicio transcodifique o rechace*: descarta
tiempo del presupuesto de SC-001 y produce errores que la persona usuaria no puede
resolver; *capturar en alta calidad y comprimir al subir*: añade latencia de CPU en el
dispositivo y un segundo paso de codificación.

---

## D-4. Persistencia local del historial

**Decision**: `drift` sobre SQLite, con una tabla `history` de campos `id` (UUID v4),
`text`, `source_lang`, `target_lang`, `confidence`, `created_at` (epoch ms UTC),
`request_id` y `outcome`. Índice por `created_at` descendente. Retención por defecto de
**200 entradas** con poda FIFO (la más antigua primero) dentro de una transacción.
Borrado total con confirmación, `DELETE` + `VACUUM` y limpieza de cachés en memoria, de
modo que el borrado sea verificable.

**Rationale**: Con 200 entradas, un `LIKE %texto%` es suficiente para buscar por contenido
(SQLite resuelve con holgura) y evita la complejidad de FTS5. `drift` ofrece consultas
tipadas, migraciones y reactividad, que es lo que necesita la búsqueda por fecha y texto.
La poda FIFO acota el almacenamiento y hace predecible el comportamiento.

**Alternatives considered**:
- *sqflite*: válido, pero más repetitivo y sin tipos; `drift` lo usa por debajo.
- *Hive*: clave-valor sin consultas relacionales; encaja mal con búsqueda por fecha.
- *Isar*: rápido, pero menos estándar y con más fricción para evolución de esquema.

---

## D-5. Síntesis de voz en el dispositivo

**Decision**: `flutter_tts` sobre el motor del sistema, con cadena de reserva de locales
`es-EC` → `es-MX` → `es-US` → `es-ES` → cualquier `es-*`. Si no hay voz disponible, la
aplicación degrada con elegancia: deshabilita el botón de reproducción con una
explicación, sin-crash. En Android, si falta el paquete de datos
(`LANG_MISSING_DATA`), se ofrece instalarlo mediante el flujo del motor; en iOS se
redirige a Ajustes → Accesibilidad → Contenido hablado → Voces.

**Rationale**: `es-EC` no está disponible de forma consistente en los motores de voz en
dispositivo: la cobertura depende del motor y de los paquetes instalados. La cadena de
reserva con prioridad latinoamericana maximiza la inteligibilidad sin bloquear la
funcionalidad cuando la voz no existe. La reproducción en voz es un complemento: el texto
es el resultado esencial, así que su ausencia no puede romper la app.

**Alternatives considered**:
- *Voz en la nube*: mejor calidad y control del locale, pero introduce dependencia de red
  en una función que debe funcionar sin conexión y costo por llamada.
- *Exigir `es-EC` sin reserva*: la traducción en voz quedaría inutilizable en una parte
  importante de los dispositivos objetivo.

**Criterio de reproducción**: la voz se detiene de inmediato a petición de la persona
usuaria, se detiene sola si el sistema interrumpe el audio (llamada entrante) y no compite
con la entrada de voz de la persona usuaria.

---

## D-6. Accesibilidad de la interfaz de resultado

**Decision**: áreas táctiles mínimas de 48×48 dp (Android) y 44×44 pt (iOS); soporte de
escalado de texto del sistema hasta el 200 % sin truncar el texto de la traducción;
contraste mínimo 4,5:1 para texto normal y 3:1 para texto grande y para indicadores que
transmiten significado; y ningún estado (error, confianza baja, progreso) señalado solo
por color: siempre texto + icono + color, con la advertencia de confianza baja en un
panel de alto contraste y anunciada como región independiente por el lector de pantalla.

**Rationale**: La persona usuaria principal lee el resultado de forma sostenida y no dispone
de la redundancia auditiva que tiene una persona oyente. Un estado que solo se distingue
por color es invisible para quien no percibe ese color o para quien navega con lector de
pantalla, y truncar el texto con elipsis puede cortar el significado de la frase.

**Alternatives considered**: *elipses en el texto traducido*: se descarta por el riesgo de
alterar el significado; *tema oscuro por defecto con contraste bajo*: se descarta porque
el contraste se mide contra el fondo real de cada estado.

---

## D-7. Privacidad: no retención del video y control de registros

**Decision**: el video se escribe solo en el directorio temporal de la aplicación y se
borra en un bloque `finally` tras el envío, el error o la cancelación; nunca en el
almacén compartido ni en los documentos de la aplicación. La tabla del historial se cifra
con SQLCipher y la clave reside en el almacén de claves del plataforma, y se excluye de
las copias de seguridad automáticas. Los registros solo incluyen metadatos no sensibles
(`request_id`, `outcome`, `confidence`, `timing.*`, `code` de error, estado HTTP) y nunca
el texto traducido, los bytes del video ni datos personales.

**Rationale**: FR-017 y FR-018 exigen no retener el video y no enviar ni mostrar
identificadores. La forma más robusta de cumplirlo es estructural: si la única ruta de
escritura posible es la caché temporal y el borrado está en el `finally`, el video no
puede sobrevivir a la operación. Cifrar el historial es proporcionado en relación al
riesgo: el texto traducido puede contener información personal de la conversación.

**Alternatives considered**:
- *Confiar solo en el cifrado de plataforma sin cifrar la base*: se acepta como plan B
  documentado si SQLCipher resulta pesado para la v1; la decisión queda como tarea de
  implementación con criterio explícito.
- *Registrar el texto traducido en modo debug*: se descarta; el registro de diagnóstico
  puede acabar en informes de fallos.
- *Clave de cifrado en preferencias*: se descarta; la clave debe residir en el almacén de
  claves.

---

## D-8. Resiliencia del cliente frente a fallos de red y de servicio

**Decision**: timeout de conexión 15 s y de lectura 60 s; reintentos automáticos de 2 para
`SERVICE_UNAVAILABLE` y `TIMEOUT`, 1 para `INTERNAL_ERROR` y `RATE_LIMITED`, 0 para el
resto; retroceso exponencial con respeto de `Retry-After` (base 1 s, techo 10 s, con
jitter); y la **misma** `Idempotency-Key` en todo reenvío de la misma muestra.

**Rationale**: SC-001 y SC-005 exigen que el resultado llegue o que el fallo se comunique
con claridad. La distinción clave es entre fallos de red (recuperables, la muestra se
conserva y se reenvía) y fallos de la muestra (el contenido no es válido, hay que regrabar:
reintentar automáticamente sería un bucle). La idempotencia evita que un reenvío genere
una segunda traducción facturada o un segundo registro en el historial del servicio.

**Alternatives considered**: *reintentar indefinidamente*: contrario a SC-005 y Costa de
datos; *descartar la muestra en cualquier error*: obliga a regrabar aunque el problema sea
la red, contradiciendo FR-011.

---

## D-9. Semántica de resultado frente a semántica de error

**Decision**: la confianza baja y el idioma inesperado son **resultados** (`HTTP 200` con
`outcome: low_confidence` / `unexpected_language`), no errores HTTP. El cliente decide con
un único enumerado `TranslationErrorCode` que cubre ambos sobres.

**Rationale**: La petición funcionó: se aceptó un video y se produjo una traducción. Un
`422` por confianza baja mezclaría "la entrada es inválida" con "el modelo no está
seguro" y rompería las herramientas que interpretan códigos de estado (CDN, gateway,
balanceador, librerías de reintento). La separación permite además que la interfaz distinga
"vuelve a grabar" de "vuelve a intentarlo".

**Alternatives considered**: *codificar la confianza baja como 422*: rejected por las
razones anteriores; *ocultar el texto cuando la confianza es baja*: se descarta, la
persona usuaria decide si le sirve, y el contrato exige no ocultar el texto (FR-013).

---

## D-10. Descubrimiento de capacidades del servicio

**Decision**: el cliente consulta `GET /v1/contract` al arrancar para leer formatos, tamaño
y duración máximos, idiomas admitidos y umbral de confianza, en lugar de tenerlos
codificados.

**Rationale**: El servicio real todavía no existe; codificar sus límites en el cliente
convertiría cada cambio del backend en un cambio de la app y en una nueva versión. Con el
descubrimiento, los límites se ajustan al vuelo y el cliente valida la muestra contra los
límites reales.

**Alternatives considered**: *constantes fijas en el cliente*: se descarta por el costo de
mantenimiento y por el riesgo de desalineación con FR-015.

---

## D-11. Ubicación de los artefactos de Spec Kit (decisión abierta)

**Decision**: **abierta, con recomendación**. Los artefactos de Spec Kit (`.specify/`,
`specs/`) están hoy un nivel por encima del repositorio git del proyecto
(`App_MIC_LSEC_con_SDD/`), de modo que la especificación no queda versionada y la
trazabilidad del Principio V de la Constitución es solo parcial. Recomendación: mover
`.specify/` y `specs/` dentro de `App_MIC_LSEC_con_SDD/` y reejecutar el toolkit desde
allí, dejando un único repositorio con el histórico de la especificación y del código.
Alternativa: inicializar un repositorio git en la raíz del workspace.

**Rationale**: la Constitución exige que cada commit referencie su artefacto de
especificación; sin versionar la especificación, esa referencia no es verificable por
histórico.

**Alternatives considered**: *dejarlo como está*: se descarta porque el histórico del
proyecto quedaría partido en dos.

---

## Fuentes y verificación

**Verificado por consulta de documentación**: API `TextToSpeech` de Android
(`isLanguageAvailable`, `ACTION_CHECK_TTS_DATA`, `ACTION_INSTALL_TTS_DATA`),
`AVSpeechSynthesisVoice` de iOS, WCAG 2.2 (contraste 4,5:1 y 3:1, tamaño de objetivo táctil),
catálogo de locales de Azure Speech (incluye `es-EC` en la nube, no de forma consistente en
dispositivo) e ISO 639-3 para el código `ecs` de la Lengua de Señas Ecuatoriana.

**No verificable sin pruebas en dispositivo**: la disponibilidad efectiva de una voz
`es-EC` en los motores instalados (depende del motor y del paquete de datos), el conjunto
exacto de voces de iOS por versión y el comportamiento de `flutter_tts` en los flujos de
instalación. Estas comprobaciones quedan como tareas de verificación en `quickstart.md`.

**Riesgos identificados**: versiones exactas de los paquetes de pub (el agente de
investigación pudo verificar la versión de Flutter y Dart, pero no el rango de versión de
cada plugin por límites de consulta de pub.dev), rendimiento de SQLCipher en dispositivos
de gama baja, y comportamiento del cliente HTTP ante pérdida de conexión a mitad del
envío. Ninguno bloquea el diseño; todos tienen tarea de verificación asociada.
