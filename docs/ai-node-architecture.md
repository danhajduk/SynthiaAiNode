# AI Node Architecture

Status: Draft architecture target
Implementation status: Not developed
Last updated: 2026-03-11

## Purpose

This document defines the initial target architecture for the Synthia AI Node.
The AI Node is a remote Synthia service paired to Core, not a Supervisor-managed local standalone addon.

Because this repository currently contains architecture planning tasks only, all runtime behavior described here is target design and not yet implemented.

## Architectural Positioning

- AI Node runs as a remote service and pairs with a Synthia Core instance.
- Synthia Core retains governance authority.
- AI Node executes node-local responsibilities (bootstrap, registration, local policy enforcement, telemetry).
- Architecture is intentionally future-proofed for additional local providers and a future runtime manager layer.

## Authority Separation

Core authority and Node execution responsibilities are intentionally separated.

- Core authority:
  - trust and approval decisions
  - baseline governance policy issuance
  - operational identity issuance
  - future governance and policy refinement
- Node execution scope:
  - bootstrap listener behavior
  - registration and trust-client behavior
  - capability declaration and local enforcement behavior
  - node status/telemetry publication

## Node/Core Responsibility Boundaries

This section defines strict ownership to keep governance centralized in Core and execution localized to the AI Node.

### Core Responsibilities

- Trust authority and trust lifecycle decisions
- Operator approval and rejection workflow
- Initial baseline policy issuance
- MQTT operational identity/token issuance
- Future governance and policy refinement ownership

### AI Node Responsibilities

- Bootstrap listening and discovery participation
- Self-introduction during registration
- Capability declaration to Core
- Local baseline policy enforcement
- Telemetry and status publication

### Core Must Not

- Assume node capabilities before the node has declared them
- Execute node-local actions on behalf of a node without explicit node participation
- Delegate global governance authority to node-side components

### AI Node Must Not

- Invent or apply global policy independent of Core
- Self-approve trust without operator/Core approval flow
- Treat undeclared capabilities as implicitly authorized

## Major Architectural Layers

### 1) Bootstrap Listener

Node-side component that connects to bootstrap discovery channels and waits for Core bootstrap advertisements.

### 2) Registration/Trust Client

Node-side component that performs API registration with Core and handles trust activation material after approval.

### 3) Capability Manager

Node-side component responsible for representing declared node capabilities and enabled provider/service configuration.

### 4) Baseline Policy Engine

Node-side component that stores and enforces initial baseline policy received from Core.

### 5) Telemetry/Status Agent

Node-side component that reports node lifecycle and operational status for Core visibility.

### 6) Future Execution Gateway (Placeholder)

Reserved layer for future normalized AI execution APIs. Included now to prevent architectural drift as execution capabilities are introduced in later phases.

## Bootstrap Flow (Phase 1)

### Required Operator Input

- `mqtt_host` (bootstrap broker host/address)
- `node_name` (human-readable node identity label)

### Bootstrap Connection Rules

- Host is exactly the operator-provided `mqtt_host`
- Port is fixed at `1884`
- Access mode is anonymous for bootstrap discovery
- Node behavior is subscribe-only during bootstrap

### Bootstrap Topic Usage And Purpose

- Bootstrap topics exist only for Core discovery advertisements
- Core publishes registration-discovery information
- Nodes consume bootstrap advertisements and do not publish on bootstrap topics

### Bootstrap Channel Restrictions

- Bootstrap on `1884` is read-only from the node perspective
- No secrets or credentials in bootstrap traffic
- No telemetry/status traffic on bootstrap topics
- No control/command traffic on bootstrap topics

## Out Of Scope For Now

- Full AI workload execution implementation
- Detailed runtime-manager/controller implementation
- Multi-provider execution orchestration
- Fine-grained capability-aware policy synthesis
- Production hardening details (performance tuning, HA topology, advanced observability pipelines)

## Notes For Future Phases

- Keep bootstrap and trust activation concerns isolated from execution concerns.
- Preserve Core-governs / Node-executes boundary as capabilities expand.
- Extend capability and policy layers without collapsing authority boundaries.
