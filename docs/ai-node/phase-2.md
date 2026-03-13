# Phase 2 — Capability Declaration and Baseline Governance

Status: Active
Implementation status: Implemented (core scope) + Partially implemented (Phase 2 extension scaffolding)
Last updated: 2026-03-12

## Goal
Allow nodes to declare their AI capabilities and receive governance policies.

## Node Responsibilities

- Ask operator which providers/services are enabled
- Build capability manifest
- Submit capability declaration to Core

## Example Capability Data

Task Families:
- task.classification.text
- task.classification.email
- task.classification.image
- task.summarization.text
- task.summarization.email
- task.generation.text
- task.generation.image

Providers:
- openai

Environment hints:
- host
- memory class
- GPU availability

## Core Responsibilities

- Validate node capability declaration
- Store capability profile
- Issue baseline governance bundle

## Lifecycle

Core implemented lifecycle path:

`trusted -> capability_setup_pending -> capability_declaration_in_progress -> capability_declaration_accepted -> operational`

Additional implemented runtime behavior:

- trusted startup can fast-path to operational when accepted capability + fresh governance + operational MQTT readiness already exist
- temporary failures in declaration/governance/readiness/telemetry can move node to `degraded`
- deterministic recovery path (`POST /api/node/recover`) returns to:
  - `operational` when prerequisites are complete
  - `capability_setup_pending` otherwise

## Phase 2 Extension (Implemented Scaffold)

Node-local scaffolding now exists for next-phase prompt controls:

- prompt/service registration persistence
- probation transitions
- execution authorization endpoint with deny-by-default behavior for unregistered prompts

This extension is implemented locally and documented in node-control API contract, but Core-side prompt registry/policy integration remains future scope.

## See Also

- [Phase 2 Implementation Plan](./phase2-implementation-plan.md)
- [Phase 2 Validation Checklist](./phase2-validation-checklist.md)
- [Phase 2 Review and Handoff](./phase2-review-handoff.md)
- [Node Control API Contract](./node-control-api-contract.md)
