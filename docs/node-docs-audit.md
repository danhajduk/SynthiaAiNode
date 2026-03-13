# Node Docs Audit

This audit classifies the current documentation set against code in `src/` and canonical platform docs in Synthia Core.

## Keep As Active Documentation

| Document | Reason |
| --- | --- |
| `README.md` | Practical repo entry point with verified run commands. |
| `docs/README.md` | Current documentation policy and ownership boundary. |
| `docs/index.md` | Current docs landing page. |
| `docs/overview.md` | Current node-owned overview. |
| `docs/architecture.md` | Current node-internal architecture summary. |
| `docs/setup.md` | Current setup instructions verified from repo scripts and runtime. |
| `docs/configuration.md` | Current verified configuration reference. |
| `docs/integration.md` | Current node-to-Core integration summary. |
| `docs/runtime.md` | Current runtime behavior summary. |
| `docs/operations.md` | Current operational runbook. |
| `docs/core-references.md` | Canonical Core reference bridge. |
| `docs/ai-node/node-control-api-contract.md` | Node-owned API contract for the local FastAPI control surface. |
| `docs/task-details.md` | Preserves the original task brief after queue normalization. |

## Keep As Historical Reference Only

| Document | Reason |
| --- | --- |
| `docs/Reasoning.txt` | Implementation journal; useful for archaeology, not current docs navigation. |
| `docs/ai-node/phase1-implementation-plan.md` | Historical planning artifact for already-implemented scope. |
| `docs/ai-node/phase1-test-checklist.md` | Historical validation checklist. |
| `docs/ai-node/phase2-implementation-plan.md` | Historical implementation artifact for Phase 2 work. |
| `docs/ai-node/phase2-review-handoff.md` | Historical handoff notes; useful if continuing that thread. |
| `docs/ai-node/phase2-validation-checklist.md` | Historical validation artifact. |
| `docs/ai-node/ui-validation-checklist.md` | Useful test checklist, but secondary to current runtime/operations docs. |
| `docs/reports/audit-2026-03-12.md` | Point-in-time audit evidence. |
| `docs/reports/core-missing-docs-audit-2026-03-12.md` | Point-in-time golden-doc gap report. |
| `docs/reports/phase-completion-audit-2026-03-12.md` | Point-in-time phase completion audit. |
| `docs/report-format.md` | Historical audit template reference, not node docs. |

## Replace With Current Top-Level Docs Or Core References

| Document | Reason |
| --- | --- |
| `docs/ai-node-architecture.md` | Stale target-architecture document that predates implemented runtime; top-level `docs/architecture.md` should be used instead. |
| `docs/node-capability-declaration.md` | Marked as planned/not developed and no longer a reliable current source; use current runtime docs plus Core references instead. |
| `docs/phase1-overview.md` | Stale planned overview superseded by current docs and Core onboarding references. |
| `docs/ai-node/phase1-overview.md` | Phase-specific onboarding summary overlaps with Core-owned onboarding/lifecycle docs. |
| `docs/ai-node/bootstrap-contract.md` | Bootstrap contract is Core-owned. |
| `docs/ai-node/lifecycle-states.md` | Generic node lifecycle belongs to Core. |
| `docs/ai-node/registration-flow.md` | Onboarding flow and approval model are Core-owned contracts. |
| `docs/ai-node/security-boundaries.md` | Shared trust and channel-boundary model should point to Core docs. |
| `docs/ai-node/trust-state.md` | Shared trust payload/state expectations should reference canonical Core contracts, with node-local storage summarized in current node docs. |
| `docs/ai-node/node-identity.md` | Node identity remains relevant, but its durable details are better summarized under current runtime/configuration docs unless a dedicated node-owned identity spec is maintained. |
| `docs/ai-node/capability-setup-pending-contract.md` | Useful local contract detail, but it should either be folded into current active docs or kept explicitly as a secondary API/runtime spec. |
| `docs/ai-node/capability-setup-validation-checklist.md` | Secondary test artifact, not primary documentation. |

## Keep Only As Mismatch Pointers Or Audit Artifacts

| Document | Reason |
| --- | --- |
| `docs/ai-node-golden-mismatch-prompt-service-phase2.md` | Open mismatch report for golden-doc drift. |
| `docs/ai-node-golden-mismatch-startup-resume-and-capability-setup.md` | Open mismatch report for startup/capability drift. |

## Roadmap And Planning Docs We Do Not Need In Primary Navigation

| Document | Reason |
| --- | --- |
| `docs/ai-node/ai-node-roadmap.md` | Roadmap only. Keep only if you still want internal planning history. |
| `docs/ai-node/phase-1.md` | Phase summary/history, not current canonical docs. |
| `docs/ai-node/phase-2.md` | Phase summary/history, not current canonical docs. |
| `docs/ai-node/phase-3.md` | Planned roadmap doc, not verified implementation docs. |
| `docs/ai-node/phase-4.md` | Planned roadmap doc, not verified implementation docs. |
| `docs/ai-node/phase-5.md` | Planned roadmap doc, not verified implementation docs. |

## Recommendation

- Keep the new top-level `docs/*.md` files as the only primary documentation surface.
- Keep `docs/ai-node/node-control-api-contract.md` as the main detailed node-owned contract doc.
- Treat `docs/ai-node/*` phase docs, validation checklists, and roadmap files as historical references only.
- Treat bootstrap, lifecycle, registration, security-boundary, and shared trust docs as Core-owned and avoid maintaining them locally.
- If you want a cleaner tree later, the best candidates to move under `docs/archive/` are the old phase docs, implementation plans, validation checklists, and stale planned docs listed above.
