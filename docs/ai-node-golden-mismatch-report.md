# AI Node New Docs vs Golden Baseline Mismatch Report

Status: Completed
Generated: 2026-03-11
Scope:
- New docs: `docs/ai-node/*.md`
- Golden baseline (content): `docs/ai-node-architecture.md`, `docs/phase1-overview.md`
- Golden baseline (documentation conventions): `/home/dan/Projects/Synthia/docs/document-index.md`

## Summary

- Total findings: 8
- Highest-risk mismatch: contract/schema drift across bootstrap, registration, and trust payload field names.
- Code verification status: Not verifiable from current repository state (AI Node runtime implementation is not present).

## Findings

### Finding 1: Bootstrap field name drift (`registration_endpoint` vs `registration_path`)

Type
Contradictory documentation

Affected files
- `docs/ai-node/bootstrap-contract.md`
- `docs/ai-node/security-boundaries.md`
- `docs/ai-node/registration-flow.md`
- `docs/ai-node-architecture.md`

What docs show
- New docs require `registration_endpoint` in bootstrap payload and URL construction.
- Golden architecture uses `registration_path` (or full registration endpoint).

Evidence
- `docs/ai-node/bootstrap-contract.md:77`
- `docs/ai-node/security-boundaries.md:60`
- `docs/ai-node/registration-flow.md:66`
- `docs/ai-node-architecture.md:152`

Why this is a mismatch
- Two field names are defined for the same contract surface, which creates schema and parser ambiguity.

Recommended fix
- Standardize to one canonical bootstrap key in all docs (or explicitly version both with deprecation guidance).

### Finding 2: Registration request version field drift (`node_version` vs `node_software_version`)

Type
Contradictory documentation

Affected files
- `docs/ai-node/registration-flow.md`
- `docs/ai-node-architecture.md`

What docs show
- New registration flow uses `node_version`.
- Golden architecture uses `node_software_version`.

Evidence
- `docs/ai-node/registration-flow.md:90`
- `docs/ai-node-architecture.md:174`

Why this is a mismatch
- API contract mismatch for a required identity field.

Recommended fix
- Select one canonical field name and update all request examples/tables accordingly.

### Finding 3: Trust activation payload schema drift

Type
Contradictory documentation

Affected files
- `docs/ai-node/registration-flow.md`
- `docs/ai-node/trust-state.md`
- `docs/ai-node-architecture.md`

What docs show
- New docs use `node_token`, `baseline_policy`, `mqtt_credentials`.
- Golden architecture defines `node_trust_token`, `initial_baseline_policy`, `operational_mqtt_identity`/token, and endpoint details.

Evidence
- `docs/ai-node/registration-flow.md:187`
- `docs/ai-node/trust-state.md:43`
- `docs/ai-node-architecture.md:211`

Why this is a mismatch
- Identity and credential payload shape differs across docs; downstream trust-state persistence and API contracts cannot be unambiguous.

Recommended fix
- Publish one canonical trust activation schema and align all flow/trust docs to that exact shape.

### Finding 4: Persisted trust state field model drift

Type
Contradictory documentation

Affected files
- `docs/ai-node/trust-state.md`
- `docs/ai-node-architecture.md`

What docs show
- New trust-state doc stores `mqtt_username`/`mqtt_password`, `baseline_policy`, `bootstrap_host`, `core_api_url`.
- Golden architecture lists `operational_mqtt_identity`/token, `baseline_policy_version`, `bootstrap_mqtt_host`, `core_api_endpoint`.

Evidence
- `docs/ai-node/trust-state.md:44`
- `docs/ai-node/trust-state.md:46`
- `docs/ai-node/trust-state.md:47`
- `docs/ai-node/trust-state.md:42`
- `docs/ai-node-architecture.md:232`
- `docs/ai-node-architecture.md:234`
- `docs/ai-node-architecture.md:235`
- `docs/ai-node-architecture.md:236`

Why this is a mismatch
- Required persisted keys differ, causing uncertainty for migration and restart behavior.

Recommended fix
- Define canonical persisted trust-state schema and include explicit aliases/migration notes if renaming fields.

### Finding 5: Lifecycle state model drift (missing `capability_setup_pending`)

Type
Stale documentation

Affected files
- `docs/ai-node/lifecycle-states.md`
- `docs/ai-node-architecture.md`

What docs show
- New lifecycle doc transitions directly `trusted -> operational`.
- Golden architecture includes `capability_setup_pending` between `trusted` and `operational`.

Evidence
- `docs/ai-node/lifecycle-states.md:31`
- `docs/ai-node/lifecycle-states.md:32`
- `docs/ai-node-architecture.md:256`
- `docs/ai-node-architecture.md:269`

Why this is a mismatch
- State machine behavior and transition semantics differ.

Recommended fix
- Either reintroduce `capability_setup_pending` in split lifecycle docs or remove it from canonical architecture with rationale.

### Finding 6: Missing status metadata in new split docs

Type
Overstated documentation

Affected files
- `docs/ai-node/phase1-overview.md`
- `docs/ai-node/bootstrap-contract.md`
- `docs/ai-node/registration-flow.md`
- `docs/ai-node/trust-state.md`
- `docs/ai-node/lifecycle-states.md`
- `docs/ai-node/security-boundaries.md`

What docs show
- New docs omit `Status`, `Implementation status`, and `Last updated` headers.
- Golden docs conventions require explicit status labels; AI Node canonical docs currently use these headers.

Evidence
- `docs/phase1-overview.md:3`
- `docs/phase1-overview.md:4`
- `docs/phase1-overview.md:5`
- `/home/dan/Projects/Synthia/docs/document-index.md:59`

Why this is a mismatch
- Reader may interpret behavior as implemented rather than planned; this is risky for architecture-only repositories.

Recommended fix
- Add document-level status headers and section-level status markers (`Planned`) to each new split doc.

### Finding 7: Missing upstream and intra-doc cross-links in split docs

Type
Missing documentation

Affected files
- `docs/ai-node/phase1-overview.md`
- `docs/ai-node/bootstrap-contract.md`
- `docs/ai-node/registration-flow.md`
- `docs/ai-node/trust-state.md`
- `docs/ai-node/lifecycle-states.md`
- `docs/ai-node/security-boundaries.md`

What docs show
- New split docs do not include `See also` navigation.
- Golden AI Node docs include cross-links to architecture/capability docs and upstream Synthia platform docs.

Evidence
- `docs/phase1-overview.md:84`

Why this is a mismatch
- Navigation and source-of-truth traceability are weaker in split docs.

Recommended fix
- Add short `See also` blocks in each split doc linking to phase, architecture, capability, and upstream platform/API docs.

### Finding 8: Markdown fence formatting defects in new split docs

Type
Stale documentation

Affected files
- `docs/ai-node/bootstrap-contract.md`
- `docs/ai-node/registration-flow.md`
- `docs/ai-node/trust-state.md`

What docs show
- Multiple code blocks close with four backticks instead of three.

Evidence
- `docs/ai-node/bootstrap-contract.md:46`
- `docs/ai-node/registration-flow.md:76`
- `docs/ai-node/registration-flow.md:94`
- `docs/ai-node/trust-state.md:70`

Why this is a mismatch
- Markdown rendering is inconsistent and can break in stricter renderers.

Recommended fix
- Normalize all fences to matching triple-backtick open/close pairs.

## Recommended Next Action

1. Resolve Findings 1-5 first (contract/state-model mismatches).
2. Then apply Findings 6-8 (status metadata, link density, markdown hygiene).
3. After alignment, regenerate this report and verify zero contradictory findings.
