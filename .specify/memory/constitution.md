<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- Modified principles: N/A (initial concrete version)
- Added sections:
  - I. Conventional Commits (NON-NEGOTIABLE)
  - II. Commit Scope and Trailers (NON-NEGOTIABLE)
  - III. Project Metrics and COCOMO (NON-NEGOTIABLE)
  - Additional Constraints: Branching/Review
  - Development Workflow: Commit/Review Gates
- Removed sections: None
- Templates requiring updates: None (project-specific)
- Follow-up TODOs: None
-->

# Proyecto Constitution

## Core Principles

### I. Conventional Commits (NON-NEGOTIABLE)

Every commit MUST follow the Conventional Commits structure:

```text
<tipo>(<alcance opcional>): <descripción corta en imperativo>

[cuerpo opcional explicativo]

[pie de página opcional]
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`. Descriptions MUST use imperative present tense in English or Spanish as appropriate, start with lowercase (unless proper nouns/siglas), have no trailing period, and be under 50 characters. If a body is needed, separate with a blank line and wrap lines to a maximum of 72 characters.

### II. Commit Scope and Trailers (NON-NEGOTIABLE)

- **Scope is mandatory for feature-related work:** Commits MUST include the functionality number as scope (e.g., `feat(001): ...`, `fix(001): ...`).
- **Deletion/Rewrite trailer required:** Commits that delete or rewrite code MUST include the trailer `Causa:` with one of `requisito|defecto|refactor` (e.g., `Causa: refactor`).
- **Issue references:** When applicable, use footers such as `Closes #<id>`, `Fixes #<id>`, or `Refs #<id>` to link commits to tracked work.

### III. Project Metrics and COCOMO (NON-NEGOTIABLE)

- **Scale factors:** The project scale factors MUST be qualified in the row `000-proyecto` of `metricas/factores-cocomo.csv`.
- **Effort multipliers:** Effort multipliers MUST be qualified at the end of each `/speckit-plan`.

## Additional Constraints

### Branching and Review

- **Atomic commits:** Each commit MUST represent a single logical change.
- **Staged review:** Before committing, changes MUST be reviewed in the staging area (e.g., via Fork's Commit panel) to ensure only intended files are included.
- **No secrets:** Secrets, keys, or credentials MUST NOT be committed.

## Development Workflow

### Commit and Review Gates

- **Message validation:** Commit messages MUST conform to Principles I and II.
- **Plan completion gate:** Before finalizing a `/speckit-plan`, COCOMO effort multipliers MUST be recorded as required by Principle III.
- **Metrics maintenance:** `metricas/factores-cocomo.csv` MUST remain up to date with the current project state.

## Governance

### Amendment Procedure

Amendments to this Constitution require:
1. A documented proposal describing the change and rationale.
2. Review and approval by the project team.
3. Update of the Constitution version according to the versioning policy below.

### Versioning Policy

- **MAJOR:** Backward incompatible governance/principle removals or redefinitions.
- **MINOR:** New principle/section added or materially expanded guidance.
- **PATCH:** Clarifications, wording, typo fixes, non-semantic refinements.

**Current Version:** 1.0.0  
**Ratified:** 2026-10-20  
**Last Amended:** 2026-10-20

### Compliance Review

All commits, plans, and process changes MUST comply with this Constitution. Deviations require explicit justification and team approval.
