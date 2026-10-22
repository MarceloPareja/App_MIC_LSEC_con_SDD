# Tasks: Traductor de Lengua de Señas Ecuatoriana (TraductorLSEC)

**Input**: Design documents from `/specs/001-traductor-lsec-streaming/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Android native structure

- [x] T001 Create project structure (`android/app/src/main/java/com/lsec/traductor/{model,view,controller}`) per implementation plan
- [x] T002 Initialize Android project with Gradle, Kotlin 1.9+, and dependencies (CameraX, Room, Retrofit, TTS) in `android/build.gradle` and `android/app/build.gradle`
- [x] T003 [P] Configure linting and formatting rules for Android Kotlin in `android/config/lint.xml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Setup Room Database schema and configuration in `android/app/src/main/java/com/lsec/traductor/model/TraductorDatabase.kt`
- [x] T005 [P] Setup Retrofit client and network configuration for cloud API communication in `android/app/src/main/java/com/lsec/traductor/controller/ApiClient.kt`
- [x] T006 [P] Configure error handling and network status monitoring infrastructure in `android/app/src/main/java/com/lsec/traductor/controller/NetworkMonitor.kt`
- [x] T007 Create base Application class and dependency wiring in `android/app/src/main/java/com/lsec/traductor/TraductorApplication.kt`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Streaming de video de señas y traducción en tiempo real (Priority: P1) 🎯 MVP

**Goal**: Permitir la captura por cámara, streaming por paquetes con ID único y duración al modelo TFLite en la nube, recepción en chat estilo WhatsApp limitado a 30 mensajes, y síntesis de voz (TTS).

**Independent Test**: Simular transmisión de paquetes de video, verificar recepción de texto traducido en chat, verificar límite estricto de 30 mensajes y activación de TTS.

### Implementation for User Story 1

- [x] T008 [P] [US1] Create MensajeTraduccion Room Entity matching table fields (`id`, `idUnicoClip`, `textoTraducido`, `marcaTemporal`, `estadoAudio`) with max 30 records FIFO policy in `android/app/src/main/java/com/lsec/traductor/model/MensajeTraduccion.kt`
- [x] T009 [P] [US1] Create MensajeDao interface for chat history queries and FIFO purge in `android/app/src/main/java/com/lsec/traductor/model/MensajeDao.kt`
- [x] T010 [US1] Implement CameraX video capture and chunk streaming controller in `android/app/src/main/java/com/lsec/traductor/controller/StreamingController.kt` (depends on T005)
- [x] T011 [US1] Implement Cloud Translation Service interacting with TFLite backend (`id_unico`, `duracion_clip_ms`, `video_chunk`) in `android/app/src/main/java/com/lsec/traductor/controller/TranslationService.kt` (depends on T005)
- [x] T012 [US1] Implement Text-to-Speech (TTS) manager in `android/app/src/main/java/com/lsec/traductor/controller/TtsManager.kt`
- [x] T013 [US1] Implement Chat ViewModel managing message history and real-time UI updates in `android/app/src/main/java/com/lsec/traductor/controller/ChatViewModel.kt` (depends on T008, T009, T011)
- [x] T014 [US1] Implement WhatsApp-like Chat UI and Camera Preview Activity/Fragment in `android/app/src/main/java/com/lsec/traductor/view/MainActivity.kt` and layout XMLs (depends on T010, T013)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (MVP ready)

---

## Phase 4: User Story 2 - Manejo de errores y baja conectividad (Priority: P2)

**Goal**: Manejar errores de red y baja conectividad de manera intuitiva y amigable para evitar confusiones en el usuario.

**Independent Test**: Simular cortes de red y baja conexión durante el streaming, verificando mensajes de error claros y reintentos automáticos.

### Implementation for User Story 2

- [x] T015 [P] [US2] Implement retry interceptor and connection state observer in `android/app/src/main/java/com/lsec/traductor/controller/NetworkRetryInterceptor.kt`
- [x] T016 [US2] Implement user-friendly error notification handler and UI feedback dialogs in `android/app/src/main/java/com/lsec/traductor/view/ErrorDialogHelper.kt`
- [x] T017 [US2] Integrate network state observation with StreamingController and ChatViewModel in `android/app/src/main/java/com/lsec/traductor/controller/StreamingController.kt` (depends on T010, T015, T016)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently with robust error handling

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, UML diagrams, validation, and optimization across all stories

- [x] T018 [P] Add comprehensive documentation and comments in Spanish across all classes in `android/app/src/main/java/com/lsec/traductor/`
- [x] T019 [P] Create UML class and sequence diagrams documentation in `docs/uml/`
- [x] T020 Run quickstart.md validation scenarios on Android device/emulator
- [x] T021 Code cleanup and performance optimization for memory footprint (<100MB)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 components for error/connectivity handling

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Models and services within a story marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently (Streaming + TFLite cloud + Chat + TTS)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Resilience & low connectivity)
4. Polish & Documentation → Final delivery
