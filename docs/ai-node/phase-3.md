# Phase 3 — Prompt Contracts and Execution Governance

## Goal
Introduce governed prompt execution.

Each prompt becomes a governed contract between the caller, Core, and AI Node.

## Prompt Metadata

- prompt_id
- prompt_name
- owner service
- task_family
- expected frequency
- privacy class
- cost sensitivity
- version

## Prompt Lifecycle

probation → active → restricted → suspended → expired

## Governance Controls

Core controls:

- prompt approval
- budget limits
- allowed models
- prompt suspension

Node enforces:

- prompt budgets
- probation limits
- usage telemetry