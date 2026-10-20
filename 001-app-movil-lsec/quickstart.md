# Quickstart: App móvil cliente para la traducción de LSEC

**Feature**: 001-app-movil-lsec | **Fecha**: 2026-10-20 | **Fase**: 1 (Design)

Guía de validación ejecutable. Cada escenario corresponde a un criterio de aceptación de
la especificación y a una regla del contrato (`contracts/inference-api.md`). Los detalles
de datos están en `data-model.md`; no se repiten aquí.

---

## 1. Prerrequisitos

| Requisito | Detalle |
|---|---|
| Flutter | 3.x con Dart 3.x, fijado en el repositorio con FVM (`.fvmrc`) |
| SDK Android | API 29 o superior; emulador o dispositivo físico con cámara y micrófono |
| Entorno de pruebas | `mock_server/` en ejecución, accesible desde el emulador en `http://10.0.2.2:8080` |
| Dispositivo físico | Requerido para validar TTS, cámara y lector de pantalla; el emulador no basta |

```bash
# Preparación del entorno
cd App_MIC_LSEC_con_SDD/mobile
flutter pub get
flutter doctor -v          # confirma cadena de herramientas de Android
```

---

## 2. Comandos de referencia

```bash
# Análisis estático y formato
cd App_MIC_LSEC_con_SDD/mobile
flutter analyze
dart format --output=none --set-exit-if-changed .

# Pruebas
flutter test                                   # unitarias y de widgets
flutter test test/unit/                        # solo unitarias
flutter test test/widget/                      # solo de widgets
flutter test integration_test/                 # flujo completo (requiere mock_server)

# Servidor simulado del servicio de inferencia
cd App_MIC_LSEC_con_SDD/mock_server
dart run server.dart                            # escucha en :8080

# Ejecución en el emulador
cd App_MIC_LSEC_con_SDD/mobile
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8080
```

---

## 3. Escenarios de validación

### S-1. Traducción en texto (User Story 1 · FR-001 a FR-004, FR-014 a FR-016)

**Precondición**: el servidor simulado está en ejecución; la aplicación tiene permisos de
cámara y micrófono concedidos.

| Paso | Acción | Resultado esperado |
|---|---|---|
| S-1.1 | Abrir la aplicación | Se muestra la acción única de captura, con etiqueta accesible y área táctil de 48×48 dp como mínimo |
| S-1.2 | Pulsar la acción de captura y mantener la seña 3 s | Se muestra el estado "capturando"; al detener, el estado "enviando" con progreso en bytes |
| S-1.3 | Esperar la respuesta | El texto traducido aparece en pantalla, completo y sin truncar |
| S-1.4 | Cancelar la captura antes de enviar | No se envía nada al servicio; la aplicación vuelve al estado inicial y el archivo temporal se borra |
| S-1.5 | Revocar el permiso de cámara y volver a capturar | La aplicación explica qué permiso falta y cómo otorgarlo; no se bloquea con un error genérico |
| S-1.6 | Grabar 1 s (por debajo del mínimo) | La aplicación informa que la grabación fue muy corta y guía para repetirla |
| S-1.7 | Grabar más de 10 s | La captura se detiene automáticamente en el máximo y el clip se envía dentro de los límites |

**Verificación automatizada**: `mobile/integration_test/capture_flow_test.dart` cubre S-1.3,
S-1.4 y S-1.6; `mobile/test/unit/capture_validation_test.dart` cubre las restricciones de
duración y tamaño.

### S-2. Reproducción en voz (User Story 2 · FR-005, FR-006)

| Paso | Acción | Resultado esperado |
|---|---|---|
| S-2.1 | Con una traducción visible, activar la reproducción | La voz empieza a leer el texto en menos de 1 s (SC-003) |
| S-2.2 | Detener la reproducción | La lectura se interrumpe de inmediato; el texto permanece visible |
| S-2.3 | Silenciar el dispositivo durante la reproducción | El sistema conserva su comportamiento; la aplicación no altera el volumen del sistema |
| S-2.4 | Repetir una traducción desde el historial | Se reproduce de nuevo sin recapturar |
| S-2.5 | Ejecutar en un dispositivo sin voz `es-EC` | La aplicación usa la voz de reserva disponible; si no hay ninguna voz `es-*`, deshabilita la reproducción con una explicación y no falla |
| S-2.6 | Recibir una llamada durante la reproducción | La reproducción se detiene y la aplicación vuelve a un estado estable |

**Verificación automatizada**: `mobile/test/unit/speech_controller_test.dart` (resolución de
locales y cadena de reserva, con dobles de `flutter_tts`); la comprobación de voz real
requiere dispositivo físico.

### S-3. Historial (User Story 3 · FR-007, FR-008, FR-009, FR-020)

| Paso | Acción | Resultado esperado |
|---|---|---|
| S-3.1 | Generar tres traducciones y abrir el historial | Aparecen ordenadas de la más reciente a la más antigua |
| S-3.2 | Buscar por un fragmento de texto | Solo aparecen las traducciones que contienen ese fragmento |
| S-3.3 | Buscar por un rango de fechas | Solo aparecen las traducciones de ese rango |
| S-3.4 | Desactivar la red y abrir el historial | Las traducciones guardadas se consultan y se reproducen sin conexión |
| S-3.5 | Generar más de 200 traducciones | Las más antiguas se podan y el total se mantiene en 200 |
| S-3.6 | Borrar todo el historial con confirmación | El conteo queda en 0, la base se compacta y la operación no se puede deshacer |

**Verificación automatizada**: `mobile/test/unit/history_dao_test.dart` (orden, búsqueda,
poda FIFO, borrado y `VACUUM`).

### S-4. Fallos recuperables y no recuperables (User Story 4 · FR-010 a FR-013)

| Paso | Acción | Resultado esperado |
|---|---|---|
| S-4.1 | Detener el servidor simulado y enviar | Mensaje comprensible de servicio no disponible; la muestra se conserva; botón de reintento visible (SC-005) |
| S-4.2 | Reintentar con el servidor detenido | Se respeta `Retry-After`; tras agotar los reintentos se ofrece reintento manual |
| S-4.3 | Volver a levantar el servidor y reintentar | La **misma** muestra se reenvía con la misma `Idempotency-Key` y se traduce (FR-011) |
| S-4.4 | Enviar con el dispositivo en modo avión | No se inicia el envío; se informa que no hay conexión; el envío se reanuda al recuperar la red |
| S-4.5 | Servidor que responde `outcome: low_confidence` | El texto se muestra **con** la marca visible de "poco fiable" y el valor de confianza; nunca se presenta como traducción segura (FR-012, SC-007) |
| S-4.6 | Servidor que responde `outcome: unexpected_language` | El texto se muestra indicando el idioma detectado; no se oculta (FR-013) |
| S-4.7 | Servidor que responde `SAMPLE_TOO_SHORT` | No hay reintento automático; se pide regrabar |
| S-4.8 | Servidor que responde `RATE_LIMITED` | Se respeta `Retry-After`; no se reenvía antes de tiempo |

**Verificación automatizada**: `mobile/test/unit/inference_client_test.dart` (códigos de
error, reintentos, idempotencia y límites de tiempo) contra el servidor simulado.

### S-5. Privacidad (FR-017, FR-018)

| Paso | Acción | Resultado esperado |
|---|---|---|
| S-5.1 | Completar una captura y un envío | Tras la operación, no queda ningún archivo de video (`.mp4`, `.webm`, `.mov`) en el directorio de la aplicación |
| S-5.2 | Revisar la petición enviada | No contiene nombre, correo, teléfono, ubicación, identificador publicitario ni número de serie |
| S-5.3 | Revisar los registros de la aplicación | No contienen el texto traducido ni bytes de video; solo `request_id`, `outcome`, `confidence`, `timing.*` y `code` |
| S-5.4 | Comprobar las copias de seguridad del dispositivo | La base del historial no aparece en las copias de seguridad automáticas |

**Verificación automatizada**: `mobile/test/unit/privacy_test.dart` (ausencia de archivos
de video tras el flujo y ausencia de contenido sensible en los registros).

### S-6. Accesibilidad (criterios de aceptación de accesibilidad)

| ID | Criterio verificable | Cómo se comprueba |
|---|---|---|
| AC-A11Y-001 | Todos los elementos interactivos tienen un área táctil de al menos 48×48 dp (Android) o 44×44 pt (iOS) | Inspección de la maqueta y prueba de widgets que miden el área táctil |
| AC-A11Y-002 | El texto del resultado se lee completo, sin truncar, con la escala de texto del sistema al 200 % | Prueba de widgets con `MediaQuery.textScaler` en 2.0 |
| AC-A11Y-003 | Contraste de texto normal ≥ 4,5:1 y de texto grande ≥ 3:1; los indicadores de estado cumplen ≥ 3:1 | Verificación con herramienta de contraste sobre los colores del tema |
| AC-A11Y-004 | Los estados "confianza baja" y "error" muestran texto, icono y color; nunca solo color | Inspección visual y simulación de daltonismo |
| AC-A11Y-005 | Botón de captura, control de reproducción, texto del resultado e ítems del historial tienen etiqueta de lector de pantalla | Prueba de semántica con TalkBack o VoiceOver |
| AC-A11Y-006 | El orden de foco es lógico: captura → resultado → reproducción → historial | Recorrido con TalkBack y navegación por teclado |
| AC-A11Y-007 | El resultado poco fiable muestra el valor de confianza y un texto de advertencia explícito en un panel de alto contraste, anunciado por separado | Prueba de widget y recorrido con lector de pantalla |
| AC-A11Y-008 | La voz se detiene de inmediato si empieza la entrada de voz de la persona usuaria, y se puede detener manualmente | Prueba de interacción |
| AC-A11Y-009 | Si no hay voz disponible, la aplicación degrada con elegancia y no falla | Prueba con doble de TTS sin voces |
| AC-A11Y-010 | Los ítems del historial se anuncian con vista previa del texto y metadatos | Prueba de semántica |

---

## 4. Criterio de éxito de la validación

La feature se considera validada cuando:

1. `flutter analyze` no reporta incidencias y `dart format` no propone cambios.
2. `flutter test` pasa sin fallos.
3. Los escenarios S-1 a S-5 se ejecutan correctamente contra el servidor simulado.
4. Los criterios AC-A11Y-001 a AC-A11Y-010 se verifican en dispositivo físico.
5. El tiempo medido desde el inicio de la captura hasta el texto en pantalla cumple
   SC-001 (p90 < 10 s) con la red del emulador simulando la latencia objetivo.
