# Implementation Plan: TraductorLSEC App Móvil

**Branch**: `002-traductor-lsec-movil` | **Date**: 2026-10-21 | **Spec**: specs/002-traductor-lsec-movil/spec.md

**Input**: Feature specification from `/specs/002-traductor-lsec-movil/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command; its definition describes the execution workflow.

## Summary

App móvil Android nativa que captura señas LSEC mediante la cámara, envía el video por streaming en paquetes a un servidor externo con modelo TFLite, y muestra la traducción en tiempo real en un chat con historial de hasta 30 traducciones, con TTS en el cliente. Sin autenticación ni almacenamiento en la nube.

## Technical Context

**Language/Version**: Kotlin (Android nativo), Java para servidor MVC
**Primary Dependencies**: Android CameraX, Retrofit/OkHttp, TensorFlow Lite (servidor), TTS Android
**Storage**: Local solo historial de chat (hasta 30 traducciones); sin nube
**Testing**: JUnit, Espresso, TDD en todas las fases antes de commit
**Target Platform**: Android (amplia compatibilidad de versiones)
**Project Type**: mobile-app + api
**Performance Goals**: Traducción en tiempo real, streaming continuo sin almacenamiento local
**Constraints**: Baja conexión, sin login, sin datos en nube, endpoint en .env
**Scale/Scope**: Historial de 30 traducciones, clips de referencia 10 min continuos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Conventional Commits con scope 002.
- MVC en servidor.
- TDD antes de commit.
- Conexión vía .env, endpoint no expuesto.
- Código en español.

## Project Structure

### Documentation (this feature)

```text
specs/002-traductor-lsec-movil/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
android/
├── app/
│   ├── src/main/java/.../camara/
│   ├── src/main/java/.../streaming/
│   ├── src/main/java/.../chat/
│   └── src/main/java/.../tts/
└── tests/

servidor/
├── src/main/java/.../controlador/
├── src/main/java/.../modelo/
├── src/main/java/.../vista/
└── tests/
```

**Structure Decision**: Mobile Android + API server con MVC, TDD.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | - | - |