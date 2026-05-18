# AI Node Standards Compliance Appendix

This appendix maps `HexeAiNode` to the Hexe node standard using repo-local evidence.

Standards source:

- [Hexe Node Standards](/home/dan/Projects/Hexe/docs/standards/Node/README.md)

Evidence in this appendix is limited to:

- implementation files in this repository
- repo-local standards-alignment documents created for this repository

## Compliance Status Vocabulary

- `Aligned`: implemented and documented with direct repo evidence
- `Partially aligned`: implemented but still needs a narrower or cleaner repo-local mapping
- `Not yet aligned explicitly`: no dedicated repo-local standards appendix or verified mapping was available before this pass

## 1. Core Node Model

Status:

- Aligned

Evidence:

- lifecycle, trust, and onboarding runtime:
  - [main.py](/home/dan/hexe/HexeAiNode/src/ai_node/main.py)
  - [onboarding_runtime.py](/home/dan/hexe/HexeAiNode/src/ai_node/runtime/onboarding_runtime.py)
  - [node_control_api.py](/home/dan/hexe/HexeAiNode/src/ai_node/runtime/node_control_api.py)
- repo-local mapping:
  - [ai-node-standards-alignment.md](/home/dan/hexe/HexeAiNode/docs/ai-node-standards-alignment.md)
  - [runtime.md](/home/dan/hexe/HexeAiNode/docs/runtime.md)

## 2. Backend Standard

Status:

- Aligned

Evidence:

- modular backend domains:
  - [src/ai_node](/home/dan/hexe/HexeAiNode/src/ai_node)
- repo-local mapping:
  - [architecture.md](/home/dan/hexe/HexeAiNode/docs/architecture.md)
  - [ai-node-standards-alignment.md](/home/dan/hexe/HexeAiNode/docs/ai-node-standards-alignment.md)

## 3. API Standard

Status:

- Aligned

Evidence:

- route implementation:
  - [node_control_api.py](/home/dan/hexe/HexeAiNode/src/ai_node/runtime/node_control_api.py)
- repo-local API family mapping:
  - [api-map.md](/home/dan/hexe/HexeAiNode/docs/api-map.md)
- deeper contract reference:
  - [node-control-api-contract.md](/home/dan/hexe/HexeAiNode/docs/ai-node/node-control-api-contract.md)

## 4. Frontend Standard

Status:

- Aligned

Evidence:

- feature-based frontend structure:
  - [frontend/src/features](/home/dan/hexe/HexeAiNode/frontend/src/features)
- extracted shared and operational helpers:
  - [formatters.js](/home/dan/hexe/HexeAiNode/frontend/src/shared/formatters.js)
  - [providerBudgetSummary.js](/home/dan/hexe/HexeAiNode/frontend/src/features/operational/providerBudgetSummary.js)
  - [clientUsageSummary.js](/home/dan/hexe/HexeAiNode/frontend/src/features/operational/clientUsageSummary.js)
  - [openaiModelPresentation.js](/home/dan/hexe/HexeAiNode/frontend/src/features/operational/openaiModelPresentation.js)
- repo-local audit:
  - [frontend-modularity-audit.md](/home/dan/hexe/HexeAiNode/docs/frontend-modularity-audit.md)

## 5. Scripts And Operations Standard

Status:

- Aligned

Evidence:

- operational baseline:
  - [bootstrap.sh](/home/dan/hexe/HexeAiNode/scripts/bootstrap.sh)
  - [run-from-env.sh](/home/dan/hexe/HexeAiNode/scripts/run-from-env.sh)
  - [stack-control.sh](/home/dan/hexe/HexeAiNode/scripts/stack-control.sh)
  - [restart-stack.sh](/home/dan/hexe/HexeAiNode/scripts/restart-stack.sh)
  - [stack.env.example](/home/dan/hexe/HexeAiNode/scripts/stack.env.example)
  - [systemd](/home/dan/hexe/HexeAiNode/scripts/systemd)
- repo-local operations mapping:
  - [operations.md](/home/dan/hexe/HexeAiNode/docs/operations.md)

Notes:

- the canonical local status path is `scripts/stack-control.sh status`
- user-systemd service names remain legacy compatibility identifiers

## 6. Background Tasks And Internal Scheduler Standard

Status:

- Aligned

Evidence:

- runtime and background ownership:
  - [scheduler-and-background-tasks.md](/home/dan/hexe/HexeAiNode/docs/scheduler-and-background-tasks.md)
- runtime modules:
  - [src/ai_node/runtime](/home/dan/hexe/HexeAiNode/src/ai_node/runtime)
  - [src/ai_node/telemetry](/home/dan/hexe/HexeAiNode/src/ai_node/telemetry)
  - [src/ai_node/execution](/home/dan/hexe/HexeAiNode/src/ai_node/execution)

## 7. Onboarding, Trust, And Readiness Standard

Status:

- Aligned

Evidence:

- onboarding and trust implementation:
  - [onboarding_runtime.py](/home/dan/hexe/HexeAiNode/src/ai_node/runtime/onboarding_runtime.py)
  - [trust_store.py](/home/dan/hexe/HexeAiNode/src/ai_node/trust/trust_store.py)
  - [node_control_api.py](/home/dan/hexe/HexeAiNode/src/ai_node/runtime/node_control_api.py)
- repo-local runtime documentation:
  - [runtime.md](/home/dan/hexe/HexeAiNode/docs/runtime.md)
  - [integration.md](/home/dan/hexe/HexeAiNode/docs/integration.md)

## 8. Persistence, Configuration, And Security Standard

Status:

- Aligned

Evidence:

- typed config and persistence stores:
  - [config](/home/dan/hexe/HexeAiNode/src/ai_node/config)
  - [persistence](/home/dan/hexe/HexeAiNode/src/ai_node/persistence)
  - [trust](/home/dan/hexe/HexeAiNode/src/ai_node/trust)
- runtime-path mapping:
  - [runtime-path-ownership.md](/home/dan/hexe/HexeAiNode/docs/runtime-path-ownership.md)
- config and sensitive-state mapping:
  - [configuration.md](/home/dan/hexe/HexeAiNode/docs/configuration.md)
  - [security-and-sensitive-state.md](/home/dan/hexe/HexeAiNode/docs/security-and-sensitive-state.md)

## 9. Provider Boundary Standard

Status:

- Aligned

Evidence:

- provider modules:
  - [providers](/home/dan/hexe/HexeAiNode/src/ai_node/providers)
  - [provider_credentials_config.py](/home/dan/hexe/HexeAiNode/src/ai_node/config/provider_credentials_config.py)
- repo-local provider-boundary mapping:
  - [provider-boundary.md](/home/dan/hexe/HexeAiNode/docs/provider-boundary.md)

## 10. Testing And Documentation Requirements

Status:

- Aligned

Evidence:

- backend tests:
  - [tests](/home/dan/hexe/HexeAiNode/tests)
- frontend targeted tests for standards-alignment extraction:
  - [formatters.test.js](/home/dan/hexe/HexeAiNode/frontend/src/shared/formatters.test.js)
  - [providerBudgetSummary.test.js](/home/dan/hexe/HexeAiNode/frontend/src/features/operational/providerBudgetSummary.test.js)
  - [clientUsageSummary.test.js](/home/dan/hexe/HexeAiNode/frontend/src/features/operational/clientUsageSummary.test.js)
  - [openaiModelPresentation.test.js](/home/dan/hexe/HexeAiNode/frontend/src/features/operational/openaiModelPresentation.test.js)
- repo-local standards docs:
  - [index.md](/home/dan/hexe/HexeAiNode/docs/index.md)
  - [ai-node-standard-compliance-summary.md](/home/dan/hexe/HexeAiNode/docs/ai-node-standard-compliance-summary.md)
  - [ai-node-standards-alignment.md](/home/dan/hexe/HexeAiNode/docs/ai-node-standards-alignment.md)

## 11. Allowed Variant Decision

Current repo-local variant decisions:

- modular backend is the canonical shape for this repo
- modular feature-based frontend is the canonical shape for this repo
- `.run/`, `data/`, and `logs/` remain an allowed runtime-path variant for this repo
- `stack-control.sh status` remains the standard local status entrypoint for this repo
- legacy protocol or service identifiers such as `X-Synthia-Admin-Token` and `synthia-ai-node-*.service` remain documented compatibility exceptions

Evidence:

- [runtime-path-ownership.md](/home/dan/hexe/HexeAiNode/docs/runtime-path-ownership.md)
- [operations.md](/home/dan/hexe/HexeAiNode/docs/operations.md)
- [api-map.md](/home/dan/hexe/HexeAiNode/docs/api-map.md)

## 12. Final Assessment

Current repo-local standards position:

- the repo is now explicitly mapped to the Hexe node standard across backend, API, frontend, operations, runtime ownership, provider boundary, scheduler behavior, and sensitive-state handling
- remaining standards work is no longer about missing major sections; it is about keeping this appendix current as implementation evolves
