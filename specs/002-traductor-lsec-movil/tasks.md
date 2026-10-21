# Tasks: TraductorLSEC App Móvil

**Input**: Design documents from `/specs/002-traductor-lsec-movil/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD obligatorio por constitución antes de commit.

**Organization**: Tasks grouped by user story.

**Estimación**: escala Fibonacci (1, 2, 3, 5, 8); los puntos son heurísticos, no ejecutados. Total planificado: 98 puntos en 30 tareas.

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Create project structure per implementation plan (3 pts)
- [ ] T002 Initialize Android Kotlin project with CameraX dependencies (5 pts)
- [ ] T003 Initialize servidor Java MVC project (5 pts)
- [ ] T004 [P] Configure .env for connection endpoint (1 pt)
- [ ] T005 [P] Configure TFLite dependency in server (3 pts)

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T006 Setup MVC folder structure in servidor (2 pts)
- [ ] T007 [P] Implement streaming packet handling (5 pts)
- [ ] T008 [P] Setup TTS permissions in Android (2 pts)
- [ ] T009 [P] Setup camera permissions in Android (2 pts)
- [ ] T010 Configure error handling messages (3 pts)

## Phase 3: User Story 1 - Capturar y enviar señas (Priority: P1) 🎯 MVP

**Goal**: Captura continua y traducción en tiempo real.

**Independent Test**: Activar grabación y verificar traducción en chat.

- [ ] T011 [P] [US1] Create Traduccion model in android/app/src/main/java/.../model/Traduccion.kt (2 pts)
- [ ] T012 [P] [US1] Create Clip model in android/app/src/main/java/.../model/Clip.kt (2 pts)
- [ ] T013 [US1] Implement camera capture service in android/app/src/main/java/.../camara/CamaraServicio.kt (5 pts)
- [ ] T014 [US1] Implement streaming sender in android/app/src/main/java/.../streaming/EnvioPaquetes.kt (5 pts)
- [ ] T015 [US1] TDD: write failing tests for clip metadata (duración+ID) before impl (2 pts)
- [ ] T015a [US1] Implement clip metadata sending in servidor/src/main/java/.../controlador/TraduccionControlador.java (5 pts)
- [ ] T016 [US1] Implement TFLite processing in servidor/src/main/java/.../modelo/ProcesadorTFLite.java (8 pts)
- [ ] T016a [US1] TDD: write failing tests for low connection handling (3 pts)
- [ ] T016b [US1] Implement low-connection throttling (limit TTS) in android/app/src/main/java/.../streaming/EnvioPaquetes.kt (5 pts)
- [ ] T017 [US1] TDD: write failing tests for error messages ("no fue posible traducir", etc.) (2 pts)
- [ ] T017a [US1] Add error messages handling (3 pts)

## Phase 4: User Story 2 - Historial de chat (Priority: P2)

**Goal**: Mostrar hasta 30 traducciones.

- [ ] T018 [P] [US2] Create chat UI in android/app/src/main/java/.../chat/ChatActivity.kt (5 pts)
- [ ] T018a [US2] TDD: write failing tests for history max 30 (2 pts)
- [ ] T019 [US2] Implement history storage (max 30) in android/app/src/main/java/.../chat/Historial.kt (3 pts)

## Phase 5: User Story 3 - TTS (Priority: P3)

**Goal**: Reproducir audio de traducción.

- [ ] T020 [P] [US3] Implement TTS service in android/app/src/main/java/.../tts/ServicioTTS.kt (3 pts)
- [ ] T020a [US3] TDD: write failing tests for permission closure (2 pts)
- [ ] T021 [US3] Request audio permissions and close app if denied (3 pts)

## Final Phase: Polish & Cross-Cutting Concerns

- [ ] T022 [P] Documentation updates (2 pts)
- [ ] T023 Code cleanup (2 pts)
- [ ] T024 Run quickstart validation (3 pts)