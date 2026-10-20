# Implementation Plan: App móvil cliente para la traducción de LSEC

**Branch**: `001-app-movil-lsec` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-app-movil-lsec/spec.md`

**Note**: Este documento es la salida de `/speckit.plan`; define el diseño técnico derivado de
`research.md`, `data-model.md` y `contracts/inference-api.md`.

## Summary

**Requisito principal**: una aplicación móvil cliente que permita a una persona sorda
capturar su seña, obtener su traducción al español en pantalla y escucharla en voz,
con un historial local consultable sin conexión.

**Enfoque técnico**: cliente Flutter (código único Android/iOS) en `mobile/`, con captura
de video con audio, subida en streaming como `multipart/form-data` a
`POST /v1/translate`, reproducción con el motor de voz del sistema y persistencia local
del historial en SQLite mediante `drift`. El servicio de inferencia es una feature
separada y todavía no existe: el cliente se define contra el contrato de
`contracts/inference-api.md` y se desarrolla contra el servidor simulado de
`mock_server/`.

**Restricción que gobierna el diseño**: SC-001 exige el texto en pantalla en menos de
10 s desde el inicio de la captura. Eso condiciona la tasa de bits de captura (clip de
0,5 a 3 MB), el mecanismo de subida (un solo viaje de ida y vuelta, en streaming) y los
tiempos de espera con reintento. La tasa de bits la fija el cliente: ningún ajuste del
servicio puede recuperar los 10 s perdidos en la subida.

**Trazabilidad**: cada requisito FR-001 a FR-020 se asigna a un módulo de `features/`, y
cada módulo a una historia de usuario de la especificación, de modo que la cobertura sea
verificable.

## Technical Context

**Language/Version**: Dart 3.x (Flutter 3.x, con FVM fijando la versión en el repositorio);
Java/Kotlin del lado Android solo a través de los plugins de plataforma

**Primary Dependencies**: `camera` (captura de video con audio), `flutter_tts` (voz del
sistema), `dio` (HTTP con streaming, timeouts y reintentos), `drift` + `drift_flutter`
(SQLite tipado), `path_provider` (rutas de caché y almacenamiento), `mocktail` (dobles de
prueba)

**Storage**: SQLite local vía `drift`, tabla `history` cifrada con SQLCipher (clave en el
almacén de claves del plataforma); el video de la captura vive solo en el directorio
temporal y se borra tras procesarse

**Testing**: `flutter_test` (unitarias y de widgets), `integration_test` (flujo completo
contra el servidor simulado) y `mocktail`; verificación manual en dispositivo para TTS,
cámara y lector de pantalla

**Target Platform**: Android 10+ (API 29) e iOS 15+, con desarrollo principal sobre
Android; emulador Android como entorno de referencia

**Project Type**: aplicación móvil (cliente) con servidor simulado de apoyo

**Performance Goals**: texto de traducción visible en menos de 10 s desde el inicio de la
captura (p90, SC-001); reproducción por voz iniciada en menos de 1 s desde que el texto
está disponible (SC-003); 95 % de las capturas de seña clara con traducción visible
(SC-002)

**Constraints**: clip entre 0,5 y 3 MB, duración entre 1,5 s y 10 s, máximo 25 MB;
tiempo de espera de lectura de 60 s y de conexión de 15 s; máximo 2 reintentos
automáticos; historial de 200 entradas; areas táctiles de 48×48 dp; escalado de texto
del sistema soportado hasta el 200 %; contraste mínimo 4,5:1; sin retención del video de
la muestra ni de datos personales

**Scale/Scope**: 1 desarrollador, 4 historias de usuario, 20 requisitos funcionales, 20
requisitos mapeados a 4 módulos de `features/`, 4 entidades, 1 servicio externo (simulado
en la v1), 3 endpoints contractuales

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution v1.0.0 (ratificada 2026-10-20). La Constitución regula el control de versiones y
los mensajes de commit; no impone stack técnico, por lo que las puertas se derivan de sus
principios y restricciones.

| Puerta | Origen | Estado | Cómo se cumple en este plan |
|--------|--------|--------|----------------------------|
| P1. Todo commit usa `tipo(alcance): descripción` en imperativo | Principio I y II | PASS | Cada tarea de `tasks.md` se mapea a un commit con tipo de la lista cerrada (`feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`) y alcance `001-app-movil-lsec` |
| P2. Un solo cambio lógico por commit | Principio IV | PASS | La unidad de commit es una tarea del plan; los refactors (`refactor`) se separan de las functionality (`feat`) y de las correcciones (`fix`) |
| P3. Trazabilidad commit ↔ spec ↔ sesión de métricas | Principio V | PASS (con reserva) | Cada commit referencia la funcionalidad `001-app-movil-lsec`; el cierre de sesión se registra en `metricas/sesiones/historico.csv` con `commit_inicio`, `commit_fin` y `commits`. **Reserva**: `specs/` y `.specify/` están hoy fuera del repositorio git, por lo que la trazabilidad no es aún verificable por commit |
| P4. No versionar material sensible ni datos personales | Restricciones de control de versiones | PASS | El código no contiene credenciales; las muestras de video, las traducciones y cualquier dato de personas sordas/oyentes son datos de ejecución, nunca se versionan; `.env` y artefactos de build quedan excluidos |
| P5. Revisión de cumplimiento en cada commit/PR | Governance | PASS | La checklist `checklists/requirements.md` y esta tabla de puertas son la referencia de revisión; toda desviación se justifica por escrito en la descripción del PR |
| P6. Sync Impact Report retirado antes de commitear la Constitución | Governance (material de revisión) | PENDIENTE | Acción previa al primer commit: eliminar el bloque `<!-- SYNC IMPACT REPORT ... -->` de `.specify/memory/constitution.md` |

Resultado de la puerta: **PASS con una reserva y una acción pendiente** (P3 y P6). La
reserva de P3 se resuelve con la decisión estructural D-4 de esta sección.

**Revaluación posterior al diseño (tras las fases 0 y 1)**: sin cambios. El diseño
incorpora las tres restricciones de la Constitución que aplican a esta feature: la
ausencia de secretos y datos personales en el repositorio (P4) se traduce en el diseño
de la tabla `history` cifrada y en la política de registros redactados; la trazabilidad
(P3) se concreta en el alcance `001-app-movil-lsec` que se usará en cada commit; y la
revisión de cumplimiento (P5) se apoya en `checklists/requirements.md` y en los criterios
de validación de `quickstart.md`.

## Project Structure

### Documentation (this feature)

```text
specs/001-app-movil-lsec/
├── plan.md              # Este archivo (salida de /speckit.plan)
├── spec.md              # Especificación (/speckit.specify)
├── research.md          # Fase 0: decisiones de investigación
├── data-model.md        # Fase 1: entidades y persistencia local
├── quickstart.md        # Fase 1: guía de validación ejecutable
├── contracts/           # Fase 1: contrato con el servicio de inferencia
│   └── inference-api.md
├── checklists/
│   └── requirements.md  # Checklist de calidad de la especificación
└── tasks.md             # Fase 2: salida de /speckit.tasks (NO creada por /speckit.plan)
```

### Source Code (repository root)

El repositorio git del proyecto es `App_MIC_LSEC_con_SDD/`. Todo el código de esta feature
vive dentro de ese repositorio.

```text
App_MIC_LSEC_con_SDD/
├── mobile/                        # Cliente móvil (único código de producto de la feature)
│   ├── lib/
│   │   ├── main.dart
│   │   ├── app/                   # Arranque, tema de alto contraste, rutas, localización es
│   │   ├── core/
│   │   │   ├── config/            # Endpoint base, timeouts, banderas de comportamiento
│   │   │   ├── error/             # Mapeo de código de error → mensaje accionable
│   │   │   └── result/            # Result<T> propio (evita dependencia de estado global)
│   │   ├── data/
│   │   │   ├── remote/            # Cliente HTTP del servicio de inferencia
│   │   │   │   ├── inference_client.dart
│   │   │   │   └── inference_dto.dart
│   │   │   └── local/             # Historial local (Drift/SQLite)
│   │   │       ├── translation_local_source.dart
│   │   │       └── translation_dao.dart
│   │   └── features/
│   │       ├── capture/           # FR-001, FR-002, FR-014, FR-015, FR-016
│   │       ├── translation/       # FR-003, FR-004, FR-012, FR-013
│   │       ├── speech/            # FR-005, FR-006
│   │       └── history/           # FR-007, FR-008, FR-009, FR-020
│   ├── test/
│   │   ├── unit/                  # Dominio, mapeo de errores, controlador de voz
│   │   ├── widget/                # Estados de UI, semántica y legibilidad
│   │   └── integration_test/      # Flujo captura → envío → resultado → voz
│   └── pubspec.yaml
├── mock_server/                   # Servicio de inferencia simulado (desarrollo y pruebas)
│   ├── server.dart
│   └── fixtures/                  # Muestras y respuestas de ejemplo
├── metricas/                      # Métricas de sesión y factores COCOMO (existente)
├── .specify/                      # Toolkit Spec Kit (pendiente de mover, ver D-4)
└── specs/001-app-movil-lsec/      # Artefactos de la feature (pendiente de mover, ver D-4)
```

**Structure Decision**: Repositorio único (`App_MIC_LSEC_con_SDD`) con la aplicación móvil en
`mobile/` (paquete raíz Flutter) y el servicio de inferencia simulado en `mock_server/`.
Se elige esta estructura por cuatro razones:

1. **Aislamiento del cliente**: `mobile/` es un proyecto autocontenido (dependencias,
   análisis estático y pruebas propias), lo que permite a `/speckit.implement` trabajar
   sobre un único árbol sin acoplarlo a las métricas del proyecto.
2. **Servidor simulado dentro del repositorio**: el servicio real de inferencia es otra
   feature (fuera de alcance), pero el cliente necesita una respuesta real durante el
   desarrollo y las pruebas de integración. `mock_server/` con *fixtures* permite
   verificar el contrato de `contracts/inference-api.md` sin depender de la nube.
3. **Trazabilidad con las métricas**: el repositorio ya contiene `metricas/`, que la
   Constitución exige actualizar al cierre de cada sesión; mantener ambas cosas en el
   mismo repositorio evita el trabajo manual de sincronizar dos historiales.
4. **Capa de presentación bajo `features/`**: cada historia de usuario de la
   especificación se corresponde con un módulo de `features/`, y los requisitos FR-001 a
   FR-020 se asignan explícitamente a esos módulos, lo que hace verificable la cobertura.

**Decisiones estructurales abiertas**:

- **D-4 (bloqueante para la trazabilidad)**: `.specify/` y `specs/` están hoy en la raíz
  del *workspace*, un nivel por encima del repositorio git, por lo que la especificación
  no queda versionada. Antes de la primera tarea de implementación se debe elegir entre
  (a) mover `.specify/` y `specs/` dentro de `App_MIC_LSEC_con_SDD/` y reejecutar el
  toolkit desde allí, o (b) inicializar un repositorio git en la raíz del *workspace*
  tratando `App_MIC_LSEC_con_SDD/` como subárbol. La opción (a) deja un único
  repositorio con el histórico de la especificación y del código; es la recomendada.
  Mientras esta decisión esté pendiente, la trazabilidad exigida por el Principio V de la
  Constitución solo queda parcialmente satisfecha (puerta P3).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Sin violaciones. La Constitución v1.0.0 no impone stack, estructura de directorios ni
patrones de diseño, de modo que ninguna decisión técnica de este plan requiere justificación
de complejidad. Las dos desviaciones de proceso detectadas (artefactos de Spec Kit fuera del
repositorio git y Sync Impact Report pendiente de retirar) no son violaciones de la
Constitución sino acciones de cumplimiento, y están registradas en la tabla de puertas y en
las decisiones abiertas.
