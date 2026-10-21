# Tasks: TraductorLSEC App Móvil

**Input**: Design documents from `/specs/002-traductor-lsec-movil/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD obligatorio por constitución antes de commit.

**Organization**: Tasks grouped by user story.

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Android Kotlin project with CameraX dependencies
- [ ] T003 Initialize servidor Java MVC project
- [ ] T004 [P] Configure .env for connection endpoint
- [ ] T005 [P] Configure TFLite dependency in server

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T006 Setup MVC folder structure in servidor
- [ ] T007 [P] Implement streaming packet handling
- [ ] T008 [P] Setup TTS permissions in Android
- [ ] T009 [P] Setup camera permissions in Android
- [ ] T010 Configure error handling messages

## Phase 3: User Story 1 - Capturar y enviar señas (Priority: P1) 🎯 MVP

**Goal**: Captura continua y traducción en tiempo real.

**Independent Test**: Activar grabación y verificar traducción en chat.

- [ ] T011 [P] [US1] Create Traduccion model in android/app/src/main/java/.../model/Traduccion.kt
- [ ] T012 [P] [US1] Create Clip model in android/app/src/main/java/.../model/Clip.kt
- [ ] T013 [US1] Implement camera capture service in android/app/src/main/java/.../camara/CamaraServicio.kt
- [ ] T014 [US1] Implement streaming sender in android/app/src/main/java/.../streaming/EnvioPaquetes.kt
- [ ] T015 [US1] TDD: write failing tests for clip metadata (duración+ID) before impl
- [ ] T015a [US1] Implement clip metadata sending in servidor/src/main/java/.../controlador/TraduccionControlador.java
- [ ] T016 [US1] Implement TFLite processing in servidor/src/main/java/.../modelo/ProcesadorTFLite.java
- [ ] T016a [US1] TDD: write failing tests for low connection handling
- [ ] T016b [US1] Implement low-connection throttling (limit TTS) in android/app/src/main/java/.../streaming/EnvioPaquetes.kt
- [ ] T017 [US1] TDD: write failing tests for error messages ("no fue posible traducir", etc.)
- [ ] T017a [US1] Add error messages handling

## Phase 4: User Story 2 - Historial de chat (Priority: P2)

**Goal**: Mostrar hasta 30 traducciones.

- [ ] T018 [P] [US2] Create chat UI in android/app/src/main/java/.../chat/ChatActivity.kt
- [ ] T018a [US2] TDD: write failing tests for history max 30
- [ ] T019 [US2] Implement history storage (max 30) in android/app/src/main/java/.../chat/Historial.kt

## Phase 5: User Story 3 - TTS (Priority: P3)

**Goal**: Reproducir audio de traducción.

- [ ] T020 [P] [US3] Implement TTS service in android/app/src/main/java/.../tts/ServicioTTS.kt
- [ ] T020a [US3] TDD: write failing tests for permission closure
- [ ] T021 [US3] Request audio permissions and close app if denied

## Final Phase: Polish & Cross-Cutting Concerns

- [ ] T022 [P] Documentation updates
- [ ] T023 Code cleanup
- [ ] T024 Run quickstart validation