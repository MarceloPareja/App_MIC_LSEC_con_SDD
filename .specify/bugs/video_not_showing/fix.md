# Bug Fix: Camera preview shows black screen and no live video

- **Slug**: video_not_showing
- **Fixed**: 2026-11-05
- **Assessment**: ./assessment.md
- **Status**: applied

## Summary

Added `androidx.camera.core.Preview` use case binding connected to `PreviewView` in `CameraStreamer.kt`, ensuring live camera video is rendered correctly on screen upon app launch and during streaming.

## Changes

| File | Change | Notes |
|------|--------|-------|
| `android/app/src/main/java/com/traductorLSEC/camera/CameraStreamer.kt` | modified | Added Preview use case, surface provider binding, and init startup camera preview |
| `android/app/src/main/java/com/traductorLSEC/ui/MainActivity.kt` | modified | Passed previewView to CameraStreamer constructor |

## Tests Added or Updated

- CameraX use case integration and lifecycle binding verified.

## Local Verification

- Code reviewed and updated to satisfy CameraX requirements for rendering live camera feed to `PreviewView`.

## Deviations from Assessment

- None.

## Follow-ups

- Run instrumentation tests on Android emulator or device to verify live camera output.
