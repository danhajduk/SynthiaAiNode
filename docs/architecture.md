# Synthia AI Node Architecture

## Scope

This document covers the architecture implemented in this repository only.

## Major Components

- `src/ai_node/main.py`: process entrypoint, lifecycle bootstrap, store wiring, and FastAPI startup.
- `src/ai_node/runtime/`: onboarding runtime, bootstrap MQTT runner, capability runner, control API, readiness checks, telemetry, and service management.
- `src/ai_node/core_api/`: HTTP clients for capability declaration and governance sync.
- `src/ai_node/providers/`: provider registry, adapters, metrics, execution router, and runtime manager.
- `src/ai_node/persistence/` and `src/ai_node/*_store.py`: local state persistence for trust, identity, capability, governance, provider reports, and prompt services.
- `frontend/`: dashboard UI for setup, status, and service controls.
- `scripts/`: local bootstrap and stack-control helpers.

## Runtime Flow

1. `main.py` loads local trust and identity state.
2. If trust exists, startup resumes through `trusted -> capability_setup_pending`.
3. If trust is missing, the node uses bootstrap MQTT discovery and onboarding runtime flow.
4. The control API exposes status, setup actions, capability submission, governance refresh, provider refresh, debug endpoints, and service restart actions.
5. Capability activation uses Core HTTP APIs, local persistence, operational MQTT readiness, and trusted status telemetry.
6. Provider runtime components manage model discovery, provider health, metrics persistence, and execution routing.

## Communication With Core

- HTTP: registration/onboarding, capability declaration, governance sync
- MQTT: bootstrap discovery and trusted operational status publication
- Local UI: FastAPI control surface consumed by the frontend dashboard

## Local Persistence And State

- `.run/bootstrap_config.json`
- `.run/trust_state.json`
- `.run/node_identity.json`
- `.run/provider_selection_config.json`
- `.run/task_capability_selection_config.json`
- `.run/capability_state.json`
- `.run/governance_state.json`
- `.run/phase2_state.json`
- `.run/prompt_service_state.json`
- `.run/provider_capability_report.json`
- `data/provider_registry.json`
- `data/provider_metrics.json`

## Provider And Service Integration

- OpenAI adapter support is implemented.
- Local providers are scaffolded through the provider adapter/runtime path.
- User-level systemd controls are exposed through the service manager for backend/frontend/node restarts.

## Failure And Recovery Model

- Invalid persisted state is rejected by validators and logged safely.
- Bootstrap connection has a timeout monitor.
- Capability/governance/readiness/telemetry failures can move the node into `degraded`.
- Recovery is exposed through the node control API and trusted startup resume path.

## Related Core References

Use [core-references.md](./core-references.md) for generic onboarding, lifecycle, governance, and MQTT platform contracts.
