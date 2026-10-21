<!-- Sync Impact Report:
- Version change: template -> 1.0.0
- Modified principles: Initialized 5 core principles for TraductorLSEC (Test-First & Usability, Documentación Integral, Arquitectura MVC & Cloud Deep Learning, Modelado UML, Idioma Español)
- Added sections: Architecture & Stack constraints, Development Workflow & Quality Gates, Governance
- Removed sections: None (scaffold placeholders replaced)
- Follow-up TODOs: None
-->

# TraductorLSEC Constitution

## Core Principles

### I. Test-First & Testing Rigor (NON-NEGOTIABLE)
Las pruebas deben definirse estrictamente antes de la implementación del código (TDD). Se pondrá especial énfasis en pruebas de usabilidad y rendimiento. Tras cada funcionalidad agregada, se deben ejecutar pruebas de regresión para garantizar la estabilidad y correcta compilación del sistema.

### II. Documentación Integral
Todo el código fuente, APIs, módulos y componentes desarrollados deben estar completamente documentados, especificando su propósito, entradas, salidas y contratos de interfaz.

### III. Arquitectura Cliente-Servidor (MVC)
El sistema adopta una arquitectura cliente-servidor estructurada bajo el patrón Modelo-Vista-Controlador (MVC), donde la aplicación móvil actúa como cliente y consume servicios e inferencias de un modelo de deep learning alojado en la nube.

### IV. Modelado UML
Todo diseño de componentes, flujos e interacciones del sistema debe estar respaldado y acompañado por diagramas UML formales (casos de uso, secuencia, clases, etc.) previo o durante la especificación técnica.

### V. Idioma y Localización en Español
Todo el código fuente, comentarios, documentación técnica y artefactos de especificación deben estar escritos estrictamente en español.

## Restricciones Arquitectónicas y Tecnológicas

La aplicación móvil está orientada a la accesibilidad, usabilidad e interacción fluida en tiempo real con modelos de deep learning en la nube. Se priorizará la separación de responsabilidades mediante MVC y la robustez en la comunicación cliente-servidor.

## Flujo de Desarrollo y Puertas de Calidad

1. **Especificación y Planificación:** Toda nueva funcionalidad requiere especificación formal mediante Spec Kit.
2. **Pruebas Primeras:** Red-Green-Refactor estricto con enfoque en rendimiento, usabilidad y pruebas automatizadas.
3. **Validación de Regresión:** Verificación de compilación y ejecución de pruebas de regresión ante cada cambio o incorporación de funcionalidad.
4. **Validación UML y Documentación:** Actualización de diagramas UML y documentación antes de dar por completada cualquier tarea o funcionalidad.

## Governance

- La Constitución supersede cualquier otra práctica de desarrollo en el repositorio.
- Las enmiendas requieren documentación, justificación y aprobación explícita mediante incremento de versión (SemVer).
- Las revisiones de cumplimiento se realizan en cada ciclo de validación de tareas y revisión de código.

**Version**: 1.0.0 | **Ratified**: 2026-10-21 | **Last Amended**: 2026-10-21
