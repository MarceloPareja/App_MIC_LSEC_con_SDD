# Tasks: TraductorLSEC

**Input**: Design documents from `/specs/001-traductor-lsec/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Mobile**: `app/src/main/java/com/traductorLSEC/`, `app/src/main/res/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Android project structure per implementation plan in `app/` (build.gradle, manifest, source dirs)
- [ ] T002 Configure Android permissions in `app/src/main/AndroidManifest.xml` (CAMERA, RECORD_AUDIO, INTERNET, ACCESS_NETWORK_STATE)
- [ ] T003 [P] Setup build dependencies in `../../app/build.gradle.kts` (CameraX/Camera2, OkHttp/WebSocket, TextToSpeech)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create base models for chat/history in `app/src/main/java/com/traductorLSEC/model/ChatMessage.kt` (text, timestamp, id)
- [ ] T005 [P] Implement in-memory chat history with max 30 in `app/src/main/java/com/traductorLSEC/model/ChatHistory.kt`
- [ ] T006 [P] Setup network client scaffolding for streaming in `app/src/main/java/com/traductorLSEC/network/StreamClient.kt` (prepare to send duration + unique ID)
- [ ] T007 [P] Setup TTS manager scaffold in `app/src/main/java/com/traductorLSEC/tts/TTSManager.kt` (request permissions, speak)
- [ ] T008 Configure error handling utilities in `app/src/main/java/com/traductorLSEC/util/ErrorHandler.kt`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Real-time sign translation (Priority: P1) 🎯 MVP

**Goal**: Stream signs via camera in packets (up to 10 min), send to remote TFLite model with duration + unique ID, receive text in real-time, display in WhatsApp-style chat, support TTS.

**Independent Test**: Stream short LSEC clip, verify text appears in chat, TTS plays audio when requested.

### Implementation for User Story 1

- [ ] T009 [P] [US1] Implement camera capture with packetization in `app/src/main/java/com/traductorLSEC/camera/CameraStreamer.kt` (CameraX/Camera2, chunk stream, no full-file storage)
- [ ] T010 [US1] Generate unique stream/session ID and track duration in `app/src/main/java/com/traductorLSEC/network/StreamSession.kt`
- [ ] T011 [US1] Integrate StreamClient to send packets with duration + unique ID to cloud model endpoint in `app/src/main/java/com/traductorLSEC/network/StreamClient.kt`
- [ ] T012 [US1] Handle real-time text responses and append to ChatHistory (max 30) in `app/src/main/java/com/traductorLSEC/network/ResponseHandler.kt`
- [ ] T013 [US1] Create WhatsApp-style chat UI in `app/src/main/java/com/traductorLSEC/ui/ChatActivity.kt` and `app/src/main/res/layout/activity_chat.xml`
- [ ] T014 [US1] Wire camera start/stop, streaming, and chat updates in `app/src/main/java/com/traductorLSEC/ui/MainActivity.kt`
- [ ] T015 [US1] Integrate TTS to speak translated text in `app/src/main/java/com/traductorLSEC/tts/TTSManager.kt` and UI controls

**Checkpoint**: User Story 1 functional and testable independently

---

## Phase 4: User Story 2 - Low connectivity resilience (Priority: P2)

**Goal**: Remain usable with low/unstable connection; clear error messages, graceful degradation, retry support.

**Independent Test**: Simulate network drops/retries; verify clear messages and recovery without crash.

### Implementation for User Story 2

- [ ] T016 [P] [US2] Add retry/backoff logic to streaming in `app/src/main/java/com/traductorLSEC/network/StreamClient.kt`
- [ ] T017 [US2] Add connection state monitoring in `app/src/main/java/com/traductorLSEC/network/ConnectivityMonitor.kt`
- [ ] T018 [US2] Enhance ErrorHandler with actionable messages in `app/src/main/java/com/traductorLSEC/util/ErrorHandler.kt`
- [ ] T019 [US2] Update UI to show network status and retry prompts in `app/src/main/java/com/traductorLSEC/ui/ChatActivity.kt`

**Checkpoint**: User Stories 1 and 2 work independently

---

## Phase 5: User Story 3 - Intuitive chat history (Priority: P3)

**Goal**: WhatsApp-style chat with history limited to last 30 translations; no login, no cloud storage of user data.

**Independent Test**: Generate >30 translations, verify only last 30 shown; confirm no auth/cloud storage used.

### Implementation for User Story 3

- [ ] T020 [P] [US3] Enforce max 30 history and eviction in `app/src/main/java/com/traductorLSEC/model/ChatHistory.kt`
- [ ] T021 [US3] Add history UI rendering with timestamps in `app/src/main/java/com/traductorLSEC/ui/ChatAdapter.kt`
- [ ] T022 [US3] Ensure no login/auth flows and no cloud persistence in `app/src/main/java/com/traductorLSEC/ui/MainActivity.kt`

**Checkpoint**: All user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories

- [ ] T023 [P] Add camera permission rationale and denial handling in `app/src/main/java/com/traductorLSEC/ui/MainActivity.kt`
- [ ] T024 [P] Add TTS permission/audio handling in `app/src/main/java/com/traductorLSEC/tts/TTSManager.kt`
- [ ] T025 Enforce 10-minute limit and user feedback in `app/src/main/java/com/traductorLSEC/camera/CameraStreamer.kt`
- [ ] T026 [P] Accessibility and UI polish for intuitive UX in `app/src/main/res/layout/activity_chat.xml`
- [ ] T027 Run quickstart validation against `specs/001-traductor-lsec/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can proceed in parallel or sequentially by priority
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories
- **User Story 2 (P2)**: May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Models before services/network
- Network/camera before UI integration
- Core implementation before polish/integration

### Parallel Opportunities

- Setup tasks T002, T003 [P]
- Foundational tasks T005, T006, T007, T008 [P]
- US1 T009 [P], US2 T016 [P], US3 T020 [P]
- Polish T023, T024, T026 [P]

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup
2. Phase 2: Foundational
3. Phase 3: User Story 1
4. Validate independently - MVP ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → MVP
3. Add User Story 2 → Resilience
4. Add User Story 3 → History polish
5. Polish phase

---

## Notes

- [P] = different files, no dependencies
- [Story] label maps tasks to user stories for traceability
- Each user story independently completable and testable
- Commit after each task or logical group following constitution (feat(001): ...)
- Model is external TFLite in cloud; client only streams and displays results
- No login, no cloud storage of user data
