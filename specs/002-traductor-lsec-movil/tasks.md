# Tasks: TraductorLSEC App Móvil

**Input**: Design documents from `/specs/002-traductor-lsec-movil/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD obligatorio por constitución antes de commit.

**Organization**: Tasks grouped by user story.

**Estimación**: escala Fibonacci (1, 2, 3, 5, 8); los puntos son heurísticos, no ejecutados. Total planificado: 98 puntos en 30 tareas.

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Create project structure per implementation plan (3 pts)
- [x] T002 Initialize Android Kotlin project with CameraX dependencies (5 pts)
- [x] T003 Initialize servidor Java MVC project (5 pts)
- [x] T004 [P] Configure .env for connection endpoint (1 pt)
- [x] T005 [P] Configure TFLite dependency in server (3 pts)

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T006 Setup MVC folder structure in servidor (2 pts)
- [x] T007 [P] Implement streaming packet handling (5 pts)
- [x] T008 [P] Setup TTS permissions in Android (2 pts)
- [x] T009 [P] Setup camera permissions in Android (2 pts)
- [x] T010 Configure error handling messages (3 pts)

## Phase 3: User Story 1 - Capturar y enviar señas (Priority: P1) 🎯 MVP

**Goal**: Captura continua y traducción en tiempo real.

**Independent Test**: Activar grabación y verificar traducción en chat.

- [x] T011 [P] [US1] Create Traduccion model in android/app/src/main/java/.../model/Traduccion.kt (2 pts)
- [x] T012 [P] [US1] Create Clip model in android/app/src/main/java/.../model/Clip.kt (2 pts)
- [x] T013 [US1] Implement camera capture service in android/app/src/main/java/.../camara/CamaraServicio.kt (5 pts)
- [x] T014 [US1] Implement streaming sender in android/app/src/main/java/.../streaming/EnvioPaquetes.kt (5 pts)
- [x] T015 [US1] TDD: write failing tests for clip metadata (duración+ID) before impl (2 pts)
- [x] T015a [US1] Implement clip metadata sending in servidor/src/main/java/.../controlador/TraduccionControlador.java (5 pts)
- [x] T016 [US1] Implement TFLite processing in servidor/src/main/java/.../modelo/ProcesadorTFLite.java (8 pts)
- [x] T016a [US1] TDD: write failing tests for low connection handling (3 pts)
- [x] T016b [US1] Implement low-connection throttling (limit TTS) in android/app/src/main/java/.../streaming/EnvioPaquetes.kt (5 pts)
- [x] T017 [US1] TDD: write failing tests for error messages ("no fue posible traducir", etc.) (2 pts)
- [x] T017a [US1] Add error messages handling (3 pts)

## Phase 4: User Story 2 - Historial de chat (Priority: P2)

**Goal**: Mostrar hasta 30 traducciones.

- [x] T018 [P] [US2] Create chat UI in android/app/src/main/java/.../chat/ChatActivity.kt (5 pts)
- [x] T018a [US2] TDD: write failing tests for history max 30 (2 pts)
- [x] T019 [US2] Implement history storage (max 30) in android/app/src/main/java/.../chat/Historial.kt (3 pts)

## Phase 5: User Story 3 - TTS (Priority: P3)

**Goal**: Reproducir audio de traducción.

- [x] T020 [P] [US3] Implement TTS service in android/app/src/main/java/.../tts/ServicioTTS.kt (3 pts)
- [x] T020a [US3] TDD: write failing tests for permission closure (2 pts)
- [x] T021 [US3] Request audio permissions and close app if denied (3 pts)

## Final Phase: Polish & Cross-Cutting Concerns

- [x] T022 [P] Documentation updates (2 pts)
- [x] T023 Code cleanup (2 pts)
- [x] T024 Run quickstart validation (3 pts)

## Phase 6: Convergence

- [x] T025 Implement missing unit tests for clip metadata (duración + ID) per US1 (missing)
- [x] T026 Implement missing unit tests for low connection handling per US1 (missing)
- [x] T027 Implement missing unit tests for error messages per US1 (missing)
- [x] T028 Implement missing unit tests for chat history max 30 per US2 (missing)
- [x] T029 Implement missing unit tests for permission closure per US3 (missing)
