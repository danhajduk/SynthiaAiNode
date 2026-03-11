# Synthia AI Node — Security Boundaries (Phase 1)

## Purpose

This document defines the security boundaries for AI Node onboarding during Phase 1.

The goal is to ensure that:

- untrusted nodes cannot gain access without approval
- secrets are never exposed through bootstrap
- Core remains the authority for trust decisions
- onboarding remains secure and predictable

These boundaries must be respected by both the AI Node implementation and Synthia Core.

---

# Trust Model

The AI Node begins with **zero trust**.

Trust is granted only after:

1. bootstrap discovery
2. successful registration request
3. explicit operator approval
4. trust activation payload from Core

Until approval occurs, the node must remain untrusted.

---

# Bootstrap Security Boundary

Bootstrap MQTT (port `1884`) is a **discovery-only channel**.

Bootstrap exists only so a node can discover where Core is located.

Bootstrap must never be used for:

- control commands
- authentication
- policy distribution
- credential exchange
- telemetry
- operational communication

Bootstrap is intentionally limited.

---

# Bootstrap Allowed Data

Bootstrap messages may contain:

| Field | Description |
|------|-------------|
| core_id | identifier of the Core instance |
| core_api_url | API endpoint location |
| registration_endpoint | endpoint for node registration |
| protocol_version | bootstrap protocol version |
| registration_open | indicates whether Core is accepting registrations |

These values are considered safe discovery metadata.

---

# Bootstrap Forbidden Data

Bootstrap messages must **never contain**:

- API tokens
- node tokens
- MQTT passwords
- authentication credentials
- baseline policies
- prompt definitions
- budget rules
- control-plane commands
- telemetry endpoints

If secrets appear on bootstrap, the design is considered broken.

---

# Anonymous MQTT Restrictions

Bootstrap MQTT allows **anonymous connections**.

Because of this, strict rules apply:

Nodes may:

- connect anonymously
- subscribe to the bootstrap topic

Nodes must not:

- publish to bootstrap topics
- subscribe to wildcard topics
- send telemetry
- send registration data

Bootstrap is strictly **Core → Node discovery**.

---

# Operator Approval Requirement

Every AI Node must be explicitly approved by an operator.

Nodes must not automatically become trusted.

Approval must occur in the Core UI.

Example approval screen:

```

New AI Node Registration

Node Name: main-ai-node
Node Type: ai-node
Hostname: ai-server

[Approve]   [Reject]

```

This step prevents rogue infrastructure nodes.

---

# Credential Issuance

Credentials must only be issued **after approval**.

Credentials include:

- node_token
- MQTT operational credentials
- baseline policy

These credentials must never appear in bootstrap messages.

They must only be delivered via secure API response.

---

# Channel Separation

Synthia must maintain strict separation between communication channels.

| Channel | Purpose |
|------|------|
| bootstrap MQTT | discovery only |
| HTTP API | registration and control plane |
| operational MQTT | trusted system communication |

Bootstrap must never evolve into a control channel.

---

# Logging Safety

Nodes must never log sensitive credentials.

Sensitive fields include:

- node_token
- mqtt_password
- policy contents
- authentication headers

Logs must redact sensitive values.

Example:

```

node_token=REDACTED
mqtt_password=REDACTED

```

---

# Trust Revocation (Future)

Future phases will introduce trust revocation.

Core may eventually be able to:

- revoke node credentials
- disable compromised nodes
- rotate authentication tokens

Phase 1 does not implement revocation yet.

---

# Phase 1 Security Principles

Phase 1 follows four core principles:

### Minimal Trust
Nodes start with zero trust.

### Explicit Approval
Operators must approve every node.

### Discovery Isolation
Bootstrap remains discovery-only.

### Secret Containment
Secrets are delivered only after approval through secure channels.

These rules protect the Synthia infrastructure from unauthorized nodes.
