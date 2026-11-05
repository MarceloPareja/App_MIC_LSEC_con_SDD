# Tasks: Modelo de Respaldo Local LSEC

**Input**: Design documents from `/specs/003-modelo-respaldo-local/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD obligatorio por constitución antes de commit.

**Organization**: Tasks grouped by user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Create project structure for local model support in android/app/src/main/
- [ ] T002 [P] Configure TensorFlow Lite dependencies in android/app/build.gradle.kts
- [ ] T003 [P] Add light TFLite model asset file in android/app/src/main/assets/lsec_model_light.tflite

---

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T004 Implement EstadoConexion entity in android/app/src/main/java/com/traductorLSEC/model/EstadoConexion.kt
- [ ] T005 [P] Implement ConnectivityObserver contract in android/app/src/main/java/com/traductorLSEC/network/ConnectivityObserver.kt
- [ ] T006 [P] Implement InferenceProcessor contract in android/app/src/main/java/com/traductorLSEC/ml/InferenceProcessor.kt

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Conmutación automática a modelo local por pérdida de conexión (Priority: P1) 🎯 MVP

**Goal**: Conmutar automáticamente al modelo TFLite local y notificar al usuario ante pérdida de conexión.

**Independent Test**: Simular desconexión de red y verificar que la app conmuta al modelo local y muestra el aviso de limitaciones.

### Tests for User Story 1 (TDD)
- [ ] T007 [P] [US1] TDD: write failing unit tests for network loss and local failover in android/app/src/test/java/com/traductorLSEC/ml/LocalModelTest.kt

### Implementation for User Story 1
- [ ] T008 [P] [US1] Implement LocalModelProcessor using TFLite in android/app/src/main/java/com/traductorLSEC/ml/LocalModelProcessor.kt
- [ ] T009 [US1] Implement network loss detection and automatic failover in android/app/src/main/java/com/traductorLSEC/network/ConnectivityManager.kt
- [ ] T010 [US1] Implement visual notification banner in android/app/src/main/java/com/traductorLSEC/ui/MainActivity.kt advising that local model may be less precise or slower

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Restauración automática al modelo en nube (Priority: P2)

**Goal**: Volver a utilizar de forma automática el modelo en la nube al restablecer la conectividad de red.

**Independent Test**: Restablecer la conexión de red tras estar en modo local y verificar que las solicitudes se enrutan nuevamente a la nube.

### Tests for User Story 2 (TDD)
- [ ] T011 [P] [US2] TDD: write failing unit tests for cloud restoration in android/app/src/test/java/com/traductorLSEC/network/CloudRestorationTest.kt

### Implementation for User Story 2
- [ ] T012 [US2] Implement network restoration detection and transition back to cloud model in android/app/src/main/java/com/traductorLSEC/network/ConnectivityManager.kt
- [ ] T013 [US2] Remove local warning banner upon cloud reconnection in android/app/src/main/java/com/traductorLSEC/ui/MainActivity.kt

**Checkpoint**: User Stories 1 and 2 work independently and collaboratively.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T014 [P] Documentation updates in specs/003-modelo-respaldo-local/quickstart.md
- [ ] T015 Code cleanup and refactoring across local ML classes
- [ ] T016 Run quickstart validation and Android Studio `.gradle.kts` compilation checks
