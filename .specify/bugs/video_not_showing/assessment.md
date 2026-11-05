# Bug Assessment: Camera preview shows black screen and no live video

- **Slug**: video_not_showing
- **Created**: 2026-11-05
- **Source**: User pasted description
- **Verdict**: valid
- **Severity**: high

## Report

Giving the app access to the camera does not show live video; it only shows a black screen and no sign of a possible error that explains it.

## Symptom

When opening `MainActivity` or attempting to stream camera feed, `PreviewView` remains black and no live camera frames are rendered to the UI. Additionally, exceptions or errors are swallowed or not surfaced to the user.

## Reproduction

1. Open the app (`MainActivity`).
2. Grant camera permissions.
3. Observe that `PreviewView` shows a black screen before and during streaming.

## Suspected Code Paths

- `android/app/src/main/java/com/traductorLSEC/camera/CameraStreamer.kt:34` — `startCamera()` only binds `ImageAnalysis` to `ProcessCameraProvider`, omitting the `Preview` use case required to render camera frames to `PreviewView`.
- `android/app/src/main/java/com/traductorLSEC/ui/MainActivity.kt:33` — `CameraStreamer` is initialized but never binds the camera preview on startup or handles preview surface attachment.

## Root Cause Hypothesis

**Confidence: High**. The `CameraStreamer` class implements `ImageAnalysis.Analyzer` and binds only `ImageAnalysis` to `ProcessCameraProvider`, without configuring or binding an `androidx.camera.core.Preview` use case connected to the `PreviewView` in `activity_main.xml`. Furthermore, `startCamera()` is only invoked when `startStreaming()` is triggered, meaning no camera session is initialized upon opening the activity.

## Proposed Remediation

**Preferred**:
1. Add `androidx.camera.core.Preview` use case configuration in `CameraStreamer.kt`.
2. Connect the `Preview` surface provider to `PreviewView`.
3. Bind both `Preview` and `ImageAnalysis` to `ProcessCameraProvider` within `cameraProvider.bindToLifecycle()`.
4. Trigger camera preview binding on activity launch (or when permissions are granted) rather than waiting solely for the record button.
5. Implement proper error callbacks and user-facing error messages in case camera initialization fails.

**Files likely to change**:
- `android/app/src/main/java/com/traductorLSEC/camera/CameraStreamer.kt`
- `android/app/src/main/java/com/traductorLSEC/ui/MainActivity.kt`

**Tests to add or update**:
- Add unit/instrumentation tests verifying camera preview binding and error handling.

## Risks & Considerations

- Ensure thread safety and proper lifecycle management when binding multiple CameraX use cases (`Preview` + `ImageAnalysis`).
- Handle hardware camera release correctly on pause/stop.

## Open Questions

- None.
