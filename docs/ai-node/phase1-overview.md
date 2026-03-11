# Synthia AI Node — Phase 1 Overview

## Purpose

Phase 1 establishes **AI Node onboarding into the Synthia system**.

This phase focuses only on:

- discovering Synthia Core
- registering the AI Node
- operator approval
- trust activation
- storing node identity and credentials

Phase 1 **does not implement any AI functionality**.

No providers, prompts, or AI execution exist in this phase.

---

# Phase 1 Responsibilities

Phase 1 must implement the following:

1. Node bootstrap discovery via MQTT
2. Node registration with Core
3. Operator approval through Core UI
4. Trust activation
5. Local storage of node trust state
6. Node lifecycle states
7. Basic node status telemetry

---

# Out of Scope (Future Phases)

The following features **must NOT be implemented in Phase 1**:

- AI execution
- OpenAI integration
- prompt registration
- provider configuration
- capability declaration
- runtime manager
- model management
- cost/budget enforcement
- task routing
- provider routing
- prompt governance
- AI budgeting

These features will be introduced in later phases.

---

# Phase 1 System Flow

The following sequence describes the onboarding flow.

```

AI Node starts
│
│ connect MQTT bootstrap
▼
Bootstrap Broker (1884)
│
│ receive Core bootstrap message
▼
Synthia Core discovered
│
│ send registration request
▼
Core creates pending node
│
│ operator approval required
▼
Operator approves node
│
│ trust activation payload
▼
Node stores trust state
│
▼
Node becomes trusted

```

---

# Phase 1 Outcome

After Phase 1 completes successfully the AI Node will:

- be registered in Core
- be approved by an operator
- possess a unique node identity
- receive a node authentication token
- receive operational MQTT credentials
- store trust state locally

At this point the node becomes **trusted infrastructure** inside the Synthia system.

The node is **not yet capable of executing AI workloads**.

---

# Phase 1 Design Principles

The following rules govern the Phase 1 implementation.

### Minimal Trust

The node begins with **no trust** and gains trust only after operator approval.

### Explicit Operator Approval

Nodes must never automatically join the system.

### Bootstrap Discovery Only

Bootstrap MQTT is used **only for discovery**, never for control or secrets.

### Deterministic State

Node lifecycle states must be explicit and logged.

### Restart Persistence

Trust state must survive restarts so nodes do not need to re-register every time.

---

# Phase 1 Success Criteria

Phase 1 is complete when the following behavior works:

1. Node connects to bootstrap MQTT
2. Node discovers Core
3. Node registers through API
4. Core marks node as pending approval
5. Operator approves node
6. Node receives trust activation
7. Node stores trust state
8. Node transitions to operational state

No AI functionality should exist at this stage.

