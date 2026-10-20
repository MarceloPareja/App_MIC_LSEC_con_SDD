---

description: "Task list template for feature implementation"
---

# Tasks: App móvil cliente para la traducción de LSEC

**Input**: Design documents from `/specs/001-app-movil-lsec/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md,
data-model.md, contracts/inference-api.md, quickstart.md

**Tests**: Se incluyen tareas de prueba. Cada historia de usuario define su criterio de
verificación independiente en `spec.md`, y `quickstart.md` fija los archivos de prueba
concretos y los escenarios S-1 a S-6, por lo que las tareas de prueba son necesarias para
materializar esa validación. Regla aplicada: los tests se escriben primero y deben fallar
antes de implementar.

**Organization**: Tasks are grouped by user story to enable independent implementation and
testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Repositorio**: `App_MIC_LSEC_con_SDD/` (el repositorio git del proyecto)
- **Cliente móvil**: `mobile/lib/`, `mobile/test/`, `mobile/integration_test/`
- **Servicio simulado**: `mock_server/`
- **Artefactos de la feature**: `specs/001-app-movil-lsec/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Resolver la decisión estructural D-4 de `plan.md`: mover `.specify/` y `specs/` dentro de `App_MIC_LSEC_con_SDD/` y reejecutar el toolkit de Spec Kit desde allí (`.specify/scripts/powershell/create-new-feature.ps1`, `setup-plan.ps1`), de modo que la especificación quede versionada en git y se cumpla el Principio V de la Constitución
- [ ] T002 Crear el esqueleto del proyecto Flutter en `App_MIC_LSEC_con_SDD/mobile/` con `flutter create --org ec.edu.espe --project-name traductor_lsec mobile`
- [ ] T003 [P] Fijar la versión de Flutter con FVM en `App_MIC_LSEC_con_SDD/.fvmrc` y añadir `.fvm/` al `.gitignore` de `App_MIC_LSEC_con_SDD/`
- [ ] T004 [P] Configurar análisis estático y formato en `App_MIC_LSEC_con_SDD/mobile/analysis_options.yaml` con el conjunto de lints estricto, y definir la configuración regional y de idioma en `App_MIC_LSEC_con_SDD/mobile/lib/l10n/app_es.arb`
- [ ] T005 [P] Declarar dependencias fijadas en `App_MIC_LSEC_con_SDD/mobile/pubspec.yaml`: `camera`, `flutter_tts`, `dio`, `drift`, `drift_flutter`, `path_provider`, `mocktail`, `sqlite3_flutter_libs`, `flutter_secure_storage`
- [ ] T006 [P] Crear el paquete Dart del servicio simulado en `App_MIC_LSEC_con_SDD/mock_server/pubspec.yaml` e implementar en `App_MIC_LSEC_con_SDD/mock_server/server.dart` los endpoints `POST /v1/translate`, `GET /v1/translate/{requestId}` y `GET /v1/contract` según `specs/001-app-movil-lsec/contracts/inference-api.md`, con las *fixtures* de respuesta en `App_MIC_LSEC_con_SDD/mock_server/fixtures/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 [P] Implementar la configuración de entorno en `App_MIC_LSEC_con_SDD/mobile/lib/core/config/app_config.dart` con la URL base por `--dart-define=API_BASE_URL`, timeout de conexión 15 s, timeout de lectura 60 s, umbral de confianza 0,5, retención de historial 200 entradas y límites de captura: "Duración mínima 1.5 s", "Duración máxima 10 s", "Tamaño máximo 25 MB", "Contenedor: MP4 (H.264 + AAC-LC)", "Frecuencia de muestreo de audio: 48 kHz, mono", clip objetivo de 0,5 a 3 MB
- [ ] T008 [P] Implementar el tipo `Result<T>` en `App_MIC_LSEC_con_SDD/mobile/lib/core/result/result.dart` y el enumerado único `TranslationErrorCode` en `App_MIC_LSEC_con_SDD/mobile/lib/core/error/translation_error_code.dart`, que cubre a la vez los códigos de error HTTP y los `outcome` `ok`, `low_confidence` y `unexpected_language`
- [ ] T009 [P] Implementar el registro de eventos con redacción en `App_MIC_LSEC_con_SDD/mobile/lib/core/logging/app_logger.dart`, que solo admite `request_id`, `outcome`, `confidence`, `timing.*`, `code` y estado HTTP, y descarta el texto traducido, los bytes de video y cualquier dato personal
- [ ] T010 [P] Implementar la traducción de errores a mensajes accionables en `App_MIC_LSEC_con_SDD/mobile/lib/core/error/error_presenter.dart`, con un mensaje por cada código de la tabla de `contracts/inference-api.md` §4.1 y la acción asociada (reintentar, regrabar o esperar)
- [ ] T011 [P] Crear la entidad de captura en `App_MIC_LSEC_con_SDD/mobile/lib/data/local/models/capture_sample.dart` con los campos y restricciones de `data-model.md` §2, incluido "hasAudioTrack: Debe ser true; si no, el envío falla con NO_AUDIO_TRACK"
- [ ] T012 [P] Crear la entidad de traducción en `App_MIC_LSEC_con_SDD/mobile/lib/data/local/models/translation.dart` con los campos y restricciones de `data-model.md` §3, incluido "confidence: Rango 0.0–1.0" y el enumerado de `outcome` `ok | low_confidence | unexpected_language`
- [ ] T013 [P] Configurar la base de datos local en `App_MIC_LSEC_con_SDD/mobile/lib/data/local/app_database.dart` con la tabla `history` y el índice `idx_history_created_at` del esquema SQL de `data-model.md` §4, cifrado SQLCipher con la clave en el almacén de claves de la plataforma y exclusión de las copias de seguridad automáticas
- [ ] T014 Implementar el cliente HTTP de inferencia en `App_MIC_LSEC_con_SDD/mobile/lib/data/remote/inference_client.dart`: subida en streaming `multipart/form-data` a `POST /v1/translate` con las partes `metadata` y `file`, `Idempotency-Key` estable por muestra, parseo de `application/problem+json` (RFC 9457) y descubrimiento de capacidades en `GET /v1/contract`
- [ ] T015 Implementar la política de reintentos en `App_MIC_LSEC_con_SDD/mobile/lib/core/network/retry_policy.dart`: 2 reintentos automáticos para `SERVICE_UNAVAILABLE` y `TIMEOUT`, 1 para `INTERNAL_ERROR` y `RATE_LIMITED`, 0 para el resto, retroceso exponencial con respeto de `Retry-After` (base 1 s, techo 10 s, con jitter)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Obtener la traducción en texto de una seña (Priority: P1) 🎯 MVP

**Goal**: Capturar la seña, enviarla al servicio de inferencia y mostrar el texto traducido
en pantalla con los estados del proceso visibles.

**Independent Test**: Con el servidor simulado en marcha, capturar una muestra de 3 s
produce un texto traducido visible en pantalla sin ninguna otra funcionalidad habilitada
(escenario S-1 de `quickstart.md`).

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] Prueba unitaria de validación de captura en `App_MIC_LSEC_con_SDD/mobile/test/unit/capture_validation_test.dart` que cubra "Duración mínima 1.5 s", "Duración máxima 10 s", "Tamaño máximo 25 MB" y la obligatoriedad de la pista de audio
- [ ] T017 [P] [US1] Prueba de contrato de `POST /v1/translate` contra `mock_server` en `App_MIC_LSEC_con_SDD/mobile/test/contract/inference_client_contract_test.dart` que valide la forma de la petición multipart, la respuesta de éxito y cada código de error de `contracts/inference-api.md` §4.1
- [ ] T018 [P] [US1] Prueba de integración del flujo captura → envío → resultado en `App_MIC_LSEC_con_SDD/mobile/integration_test/capture_flow_test.dart` que cubra el resultado visible, la cancelación sin envío y el rechazo por muestra demasiado corta

### Implementation for User Story 1

- [ ] T019 [P] [US1] Implementar el servicio de captura en `App_MIC_LSEC_con_SDD/mobile/lib/features/capture/capture_service.dart`: grabación con audio, contenedor MP4 (H.264 + AAC-LC), audio mono a 48 kHz, tasa de bits ajustada al clip objetivo de 0,5 a 3 MB, parada automática en la duración máxima de 10 s, escritura solo en el directorio temporal y borrado del archivo en un bloque `finally`
- [ ] T020 [P] [US1] Implementar la gestión de permisos en `App_MIC_LSEC_con_SDD/mobile/lib/features/capture/permission_handler.dart`, con explicación de qué permiso falta y cómo otorgarlo, sin bloquear con un error genérico
- [ ] T021 [US1] Implementar el controlador de captura en `App_MIC_LSEC_con_SDD/mobile/lib/features/capture/capture_controller.dart` con los estados `idle`, `capturing`, `uploading`, `translating`, `succeeded`, `failed` y `failed_offline`
- [ ] T022 [US1] Implementar la pantalla de captura en `App_MIC_LSEC_con_SDD/mobile/lib/features/capture/capture_screen.dart` con la acción única de captura, el estado siempre visible (FR-003) y la cancelación antes del envío sin envío alguno
- [ ] T023 [US1] Implementar la presentación del resultado en `App_MIC_LSEC_con_SDD/mobile/lib/features/translation/result_view.dart` con el texto completo sin truncar y los indicadores de `outcome`
- [ ] T024 [US1] Implementar el controlador de traducción en `App_MIC_LSEC_con_SDD/mobile/lib/features/translation/translation_controller.dart`, que aplica el mapeo de errores, reintenta con la misma muestra y la misma `Idempotency-Key`, y conserva la muestra cuando el fallo es recuperable
- [ ] T025 [US1] Implementar el guardado en el historial en `App_MIC_LSEC_con_SDD/mobile/lib/data/local/translation_dao.dart`: inserción de la traducción y poda FIFO que mantiene "Retención máxima: 200 entradas"
- [ ] T026 [US1] Aplicar la pasada de accesibilidad en `App_MIC_LSEC_con_SDD/mobile/lib/features/capture/capture_screen.dart` y `App_MIC_LSEC_con_SDD/mobile/lib/features/translation/result_view.dart`: áreas táctiles de 48×48 dp, escalado de texto del sistema hasta el 200 % sin truncar, contraste de texto ≥ 4,5:1, y etiquetas de lector de pantalla

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Escuchar la traducción en voz (Priority: P2)

**Goal**: Reproducir en voz el texto traducido, con control inmediato de parada y reserva
automática de locale cuando el dispositivo no ofrece voz `es-EC`.

**Independent Test**: Con una traducción ya visible, activar la reproducción por voz y
escuchar la lectura del texto; repetirla desde el historial sin recapturar (escenario S-2
de `quickstart.md`).

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T027 [P] [US2] Prueba unitaria de la cadena de reserva de locales y de la degradación sin voz en `App_MIC_LSEC_con_SDD/mobile/test/unit/speech_controller_test.dart`, con la cadena `es-EC` → `es-MX` → `es-US` → `es-ES` → cualquier `es-*`
- [ ] T028 [P] [US2] Prueba de widget de los controles de reproducción en `App_MIC_LSEC_con_SDD/mobile/test/widget/speech_controls_test.dart`: inicio, parada inmediata, repetición y estado deshabilitado sin voz disponible

### Implementation for User Story 2

- [ ] T029 [US2] Implementar el controlador de voz en `App_MIC_LSEC_con_SDD/mobile/lib/features/speech/speech_controller.dart` con `flutter_tts`: comprobación de disponibilidad de la voz, cadena de reserva de locales, flujo de instalación de datos de voz en Android y redirección a Ajustes en iOS, parada inmediata a petición y por interrupción del sistema
- [ ] T030 [US2] Implementar las preferencias de reproducción en `App_MIC_LSEC_con_SDD/mobile/lib/features/speech/speech_preferences.dart` con los campos de `data-model.md` §5: `voiceEnabled`, `autoSpeak`, `locale`, `speechRate` (Rango 0,5–2,0), `pitch` (Rango 0,5–2,0) y `volume` (Rango 0,0–1,0)
- [ ] T031 [US2] Implementar el control de reproducción en `App_MIC_LSEC_con_SDD/mobile/lib/features/speech/speech_button.dart` con área táctil de 48×48 dp, etiquetas de lector de pantalla "Reproducir traducción" y "Detener reproducción", y estado deshabilitado con explicación cuando no hay voz
- [ ] T032 [US2] Integrar la reproducción automática en `App_MIC_LSEC_con_SDD/mobile/lib/features/translation/translation_controller.dart` cuando `autoSpeak` esté activo, sin lectura automática en el resto de casos
- [ ] T033 [US2] Integrar el botón de reproducción en `App_MIC_LSEC_con_SDD/mobile/lib/features/translation/result_view.dart` manteniendo el texto visible durante la reproducción

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Revisar traducciones anteriores (Priority: P3)

**Goal**: Consultar, buscar y reproducir las traducciones guardadas, incluso sin conexión,
con borrado total definitivo.

**Independent Test**: Con traducciones ya generadas, el historial las lista ordenadas, permite
buscarlas por texto y por fecha y reproducirlas con el dispositivo sin conexión (escenario
S-3 de `quickstart.md`).

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T034 [P] [US3] Prueba unitaria del DAO de historial en `App_MIC_LSEC_con_SDD/mobile/test/unit/history_dao_test.dart`: orden `created_at` descendente, búsqueda por texto con `LIKE`, búsqueda por rango de fechas, poda FIFO con "Retención máxima: 200 entradas" y borrado total con `VACUUM`
- [ ] T035 [P] [US3] Prueba de widget del historial en `App_MIC_LSEC_con_SDD/mobile/test/widget/history_screen_test.dart`: listado, búsqueda, consulta sin conexión y etiquetas de lector de pantalla con vista previa del texto y metadatos

### Implementation for User Story 3

- [ ] T036 [US3] Implementar la fuente local de traducciones en `App_MIC_LSEC_con_SDD/mobile/lib/data/local/translation_local_source.dart` con las consultas de `data-model.md` §4, incluida la poda dentro de una transacción
- [ ] T037 [US3] Implementar la pantalla de historial en `App_MIC_LSEC_con_SDD/mobile/lib/features/history/history_screen.dart` y su controlador en `App_MIC_LSEC_con_SDD/mobile/lib/features/history/history_controller.dart`, con lectura sin conexión
- [ ] T038 [US3] Implementar el diálogo de borrado en `App_MIC_LSEC_con_SDD/mobile/lib/features/history/history_delete_dialog.dart` con confirmación explícita, borrado irreversible, `VACUUM` y limpieza de cachés en memoria
- [ ] T039 [US3] Integrar la apertura del detalle y su reproducción en `App_MIC_LSEC_con_SDD/mobile/lib/features/history/history_screen.dart` reutilizando el control de voz de la User Story 2

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Comprender y recuperar un fallo de forma clara (Priority: P4)

**Goal**: Comunicar todo fallo con un mensaje accionable, conservar la muestra cuando el
problema es recuperable y no presentar nunca una traducción poco fiable como segura.

**Independent Test**: Simulando fallo del servicio, sin conexión y respuesta de baja
confianza, la aplicación muestra un mensaje comprensible, ofrece reintentar y conserva la
muestra (escenario S-4 de `quickstart.md`).

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T040 [P] [US4] Prueba unitaria de resiliencia del cliente en `App_MIC_LSEC_con_SDD/mobile/test/unit/inference_client_test.dart`: reintentos por código, respeto de `Retry-After`, estabilidad de la `Idempotency-Key`, timeout de lectura de 60 s y ausencia de reintento automático para los códigos de regrabado
- [ ] T041 [P] [US4] Prueba unitaria de invariantes de privacidad en `App_MIC_LSEC_con_SDD/mobile/test/unit/privacy_test.dart`: ausencia de archivos de video tras el flujo y ausencia de texto traducido o datos personales en los registros

### Implementation for User Story 4

- [ ] T042 [US4] Implementar el monitor de conectividad en `App_MIC_LSEC_con_SDD/mobile/lib/core/network/connectivity_monitor.dart` con detección de ausencia de red y reanudación automática del envío al recuperarla
- [ ] T043 [US4] Implementar la vista de fallo en `App_MIC_LSEC_con_SDD/mobile/lib/features/translation/failure_view.dart` con el mensaje del presentador de errores, la acción de reintento y la nuncación explícita de que la muestra se conservó
- [ ] T044 [US4] Añadir el indicador de confianza baja en `App_MIC_LSEC_con_SDD/mobile/lib/features/translation/result_view.dart` con texto, icono y color, el valor de confianza y la advertencia como región independiente para el lector de pantalla
- [ ] T045 [US4] Añadir el indicador de idioma inesperado en `App_MIC_LSEC_con_SDD/mobile/lib/features/translation/result_view.dart` mostrando el idioma detectado sin ocultar el texto
- [ ] T046 [US4] Integrar la reanudación automática del envío en `App_MIC_LSEC_con_SDD/mobile/lib/features/translation/translation_controller.dart` cuando la red se recupere y la muestra siga disponible

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T047 [P] Verificar en dispositivo físico los criterios AC-A11Y-001 a AC-A11Y-010 de `quickstart.md` §S-6 y registrar el resultado en `App_MIC_LSEC_con_SDD/mobile/README.md`
- [ ] T048 [P] Medir la latencia de captura a texto en pantalla contra el servidor simulado y comprobar SC-001 (p90 < 10 s) y SC-003 (voz iniciada en menos de 1 s); registrar los resultados en `App_MIC_LSEC_con_SDD/mobile/README.md`
- [ ] T049 [P] Documentar la ejecución del cliente y del servidor simulado en `App_MIC_LSEC_con_SDD/README.txt.txt`
- [ ] T050 [P] Añadir la verificación de análisis estático y pruebas en `.github/workflows/quality.yml` del repositorio `App_MIC_LSEC_con_SDD/`
- [ ] T051 Ejecutar la validación completa de `specs/001-app-movil-lsec/quickstart.md` (escenarios S-1 a S-6) y anotar los resultados
- [ ] T052 Eliminar el bloque `<!-- SYNC IMPACT REPORT ... -->` de `App_MIC_LSEC_con_SDD/.specify/memory/constitution.md` antes de versionar la Constitución (puerta P6 de `plan.md`)
- [ ] T053 Registrar el rango de commits de la sesión en `App_MIC_LSEC_con_SDD/metricas/sesiones/historico.csv` con los campos `commit_inicio`, `commit_fin` y `commits`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Integra el controlador de traducción de US1 y la política de reintentos de la fase fundacional

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Prueba unitaria de validación de captura en App_MIC_LSEC_con_SDD/mobile/test/unit/capture_validation_test.dart"
Task: "Prueba de contrato de POST /v1/translate contra mock_server en App_MIC_LSEC_con_SDD/mobile/test/contract/inference_client_contract_test.dart"
Task: "Prueba de integración del flujo captura → envío → resultado en App_MIC_LSEC_con_SDD/mobile/integration_test/capture_flow_test.dart"

# Launch all models for User Story 1 together:
Task: "Implementar el servicio de captura en App_MIC_LSEC_con_SDD/mobile/lib/features/capture/capture_service.dart"
Task: "Implementar la gestión de permisos en App_MIC_LSEC_con_SDD/mobile/lib/features/capture/permission_handler.dart"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **Commits (Constitución v1.0.0)**: cada tarea se confirma como un commit atómico con
  Conventional Commits y alcance `001-app-movil-lsec` (por ejemplo
  `feat(001-app-movil-lsec): agrega captura de video con audio`). Los cambios de formato
  (`style`) y las correcciones (`fix`) van en commits separados, y ningún commit incluye
  secretos, credenciales ni datos personales
- **Tarea bloqueante T001**: hasta que los artefactos de Spec Kit no estén dentro del
  repositorio git, la trazabilidad exigida por el Principio V de la Constitución es solo
  parcial y el commit de la especificación no puede cerrar el ciclo
