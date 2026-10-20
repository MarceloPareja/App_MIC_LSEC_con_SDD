---
description: "Task list for TraductorLSEC Android application implementation"
---

# Tasks: TraductorLSEC

**Input**: Design documents from `/specs/001-traductor-lsec/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/traductor-api-contract.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story, following Test-First (TDD) and strict Spanish language standards.

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for Android native development

- [ ] T001 Create project structure (`app/src/main/java/com/lsec/traductor/controlador`, `modelo`, `vista`) per implementation plan
- [ ] T002 Initialize Android project with Kotlin 1.9+, Jetpack CameraX, Room, and Retrofit dependencies in `app/build.gradle.kts`
- [ ] T003 [P] Configure linting, formatting, and Spanish language checks per project constitution in `app/build.gradle.kts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Setup Room database schema (`BaseDatosLsec.kt`) and local cache tables for `SolicitudTraduccion` in `app/src/main/java/com/lsec/traductor/modelo/BaseDatosLsec.kt`
- [ ] T005 [P] Implement network connectivity manager and network status observer in `app/src/main/java/com/lsec/traductor/controlador/ConexionControlador.kt`
- [ ] T006 [P] Configure Retrofit client and API interface (`TraductorApiService.kt`) for TFLite cloud service in `app/src/main/java/com/lsec/traductor/modelo/TraductorApiService.kt`
- [ ] T007 Create base data models (`SolicitudTraduccion.kt`, `ResultadoTraduccion.kt`, `ConfiguracionApp.kt`) with validation constraints in `app/src/main/java/com/lsec/traductor/modelo/`
- [ ] T008 Configure application error handling, logging in Spanish, and exception management in `app/src/main/java/com/lsec/traductor/controlador/ManejadorErrores.kt`
- [ ] T009 Setup Android Manifest permissions (camera, internet, storage) in `app/src/main/AndroidManifest.xml`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Traducción en Tiempo Real de Video en Vivo (Priority: P1) 🎯 MVP

**Goal**: Capture live video using CameraX (up to 10 min / 600 seconds) and process it via the cloud TFLite model to return real-time text translation and speech audio without requiring user sign-in.

**Independent Test**: Can be fully tested by opening the live camera recording mode, capturing a test signing video, and verifying that the system displays translated text and plays audio output.

### Tests for User Story 1 (Test-First / TDD) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Unit test for CameraX recording lifecycle and duration limits ($\le$ 600 seconds) in `app/src/test/java/com/lsec/traductor/CamaraControladorTest.kt`
- [ ] T011 [P] [US1] Integration test for live video translation workflow in `app/src/androidTest/java/com/lsec/traductor/TraduccionEnVivoTest.kt`

### Implementation for User Story 1

- [ ] T012 [P] [US1] Implement CameraX wrapper and recording controller in `app/src/main/java/com/lsec/traductor/controlador/CamaraControlador.kt`
- [ ] T013 [P] [US1] Implement text display and audio synthesis playback manager in `app/src/main/java/com/lsec/traductor/controlador/TraduccionControlador.kt`
- [ ] T014 [US1] Implement Live Translation Activity / Fragment (`TraduccionEnVivoActivity.kt`) in `app/src/main/java/com/lsec/traductor/vista/TraduccionEnVivoActivity.kt`
- [ ] T015 [US1] Integrate repository, API service, and UI controller for live video processing in `app/src/main/java/com/lsec/traductor/controlador/ProcesoTraduccionControlador.kt`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (MVP ready).

---

## Phase 4: User Story 2 - Envío de Video Grabado Previamente (Priority: P2)

**Goal**: Allow users to select existing video files from device gallery (up to 10 min / 600 seconds) and send them for automated translation without authentication.

**Independent Test**: Can be tested by selecting a saved video from the device gallery and submitting it, verifying successful translation output in text and audio.

### Tests for User Story 2 (Test-First / TDD) ⚠️

- [ ] T016 [P] [US2] Unit test for video gallery picker and file duration validator ($\le$ 600 seconds) in `app/src/test/java/com/lsec/traductor/GaleriaControladorTest.kt`

### Implementation for User Story 2

- [ ] T017 [P] [US2] Implement gallery video selector and file validator controller in `app/src/main/java/com/lsec/traductor/controlador/GaleriaControlador.kt`
- [ ] T018 [US2] Implement Gallery Selection Activity / Fragment (`SeleccionGaleriaActivity.kt`) in `app/src/main/java/com/lsec/traductor/vista/SeleccionGaleriaActivity.kt`
- [ ] T019 [US2] Integrate video upload repository with pre-recorded video handling in `app/src/main/java/com/lsec/traductor/modelo/VideoRepositorio.kt`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Operación con Baja Conexión y Resiliencia (Priority: P3)

**Goal**: Manage network intermitency transparently through local queuing, automatic retries, and synchronization background workers.

**Independent Test**: Can be tested by simulating poor network conditions or offline state during video submission, verifying local queue persistence and automatic retry upon reconnection.

### Tests for User Story 3 (Test-First / TDD) ⚠️

- [ ] T020 [P] [US3] Unit test for Room queue persistence and WorkManager retry worker in `app/src/test/java/com/lsec/traductor/ResilienciaRedTest.kt`

### Implementation for User Story 3

- [ ] T021 [P] [US3] Implement Room DAO (`SolicitudDao.kt`) for pending translation requests in `app/src/main/java/com/lsec/traductor/modelo/SolicitudDao.kt`
- [ ] T022 [US3] Implement WorkManager background worker (`SincronizacionWorker.kt`) for automatic retries in `app/src/main/java/com/lsec/traductor/controlador/SincronizacionWorker.kt`
- [ ] T023 [US3] Integrate network state notifications and offline queue feedback in `app/src/main/java/com/lsec/traductor/vista/EstadoRedActivity.kt`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T024 [P] Update documentation in `docs/` and verify all Spanish nomenclature across the project
- [ ] T025 Code cleanup, refactoring, and static analysis verification
- [ ] T026 Performance optimization (memory footprint and latency targets <5s) across all views
- [ ] T027 Run quickstart.md validation scenarios and complete regression test suite

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 common controllers but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with Room storage and network manager established in foundational phase

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Models before controllers/services
- Services before UI views/activities
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models and controllers within a story marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Live Camera Translation)
4. **STOP and VALIDATE**: Test User Story 1 independently via quickstart.md
5. Deploy/demo MVP increment

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP deployed
3. Add User Story 2 (Gallery Video) → Test independently → Deploy/Demo
4. Add User Story 3 (Offline Resilience / Low Connection) → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (Test-First discipline)
- Strict compliance with Spanish nomenclature and MVC client-server architecture
