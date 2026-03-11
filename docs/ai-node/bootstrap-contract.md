# Synthia AI Node — Bootstrap Contract

## Purpose

The bootstrap contract defines how an untrusted AI Node discovers Synthia Core.

Bootstrap exists only for:

- Core discovery
- registration metadata delivery

Bootstrap does **not** exist for:

- control messages
- telemetry
- secrets
- operational policy
- prompt registration
- AI requests

Bootstrap is intentionally narrow.

---

# Bootstrap Connection Rules

An unregistered AI Node connects to the bootstrap broker using the following fixed rules:

- **host**: user provided
- **port**: `1884`
- **authentication**: anonymous
- **client identity**: node name

The node name is used only as the node’s bootstrap identity.

It is **not** a trusted credential.

---

# Bootstrap Topic

The node must subscribe to this exact topic:

```text
synthia/bootstrap
````

Rules:

* exact topic only
* wildcard subscribe is not allowed
* nodes must not publish to bootstrap
* nodes must treat bootstrap as read-only

---

# Core Bootstrap Publisher Role

Core is responsible for publishing the bootstrap advertisement.

Only Core should publish on the bootstrap topic.

Core should publish the bootstrap payload periodically so newly started nodes can discover the system without requiring a Core restart.

Bootstrap publication should be treated as a standing discovery beacon.

---

# Bootstrap Payload

The bootstrap payload must contain only the information needed for a node to begin registration.

Required fields:

* `core_id`
* `core_api_url`
* `registration_endpoint`
* `protocol_version`
* `registration_open`

Example payload:

```json
{
  "core_id": "core-main",
  "core_api_url": "http://192.168.1.50:9001",
  "registration_endpoint": "/api/nodes/register",
  "protocol_version": 1,
  "registration_open": true
}
```

---

# Payload Requirements

Bootstrap payloads must be:

* minimal
* non-sensitive
* easy to validate
* stable enough for first-time onboarding

Bootstrap payloads must **not** include:

* node tokens
* MQTT passwords
* API secrets
* baseline policy
* prompt rules
* telemetry credentials
* any trusted operational identity material

If any such data appears in bootstrap, that is a design violation.

---

# Node Validation Rules

When a node receives a bootstrap payload, it must validate:

* payload is valid JSON or valid expected message format
* all required fields are present
* `registration_open` is true
* `protocol_version` is supported
* `core_api_url` is non-empty
* `registration_endpoint` is non-empty

If validation fails, the node must ignore the message and continue listening.

The node must not partially trust malformed bootstrap data.

---

# Protocol Version Handling

The bootstrap payload must include a protocol version so the node can determine whether it understands the advertised registration flow.

If the protocol version is unsupported, the node must:

* reject that bootstrap message
* log the mismatch
* remain in bootstrap listening state

---

# Registration Closed Behavior

If the payload indicates:

```text
registration_open = false
```

the node must not attempt registration.

It may:

* remain subscribed
* wait for a later valid message
* surface status that registration is currently closed

---

# Bootstrap Freshness

Bootstrap messages should be treated as ephemeral discovery signals.

The node should not permanently trust bootstrap data without successful API registration.

Bootstrap data may be cached briefly for convenience during onboarding, but it must not be treated as durable trust state.

Durable trust begins only after successful registration and approval.

---

# Node Behavior Summary

An untrusted node must perform the following sequence:

1. connect anonymously to the user-provided MQTT host on port `1884`
2. subscribe to `synthia/bootstrap`
3. wait for a valid Core bootstrap payload
4. validate payload contents
5. begin registration over API

The node must never:

* publish on bootstrap
* send telemetry on bootstrap
* use bootstrap as an operational message bus
* accept secrets from bootstrap

---

# Security Boundary

Bootstrap is a **discovery-only lane**.

This boundary must remain strict:

## Allowed on bootstrap

* Core presence
* Core API location
* registration endpoint
* protocol version
* registration-open state

## Not allowed on bootstrap

* secrets
* node-auth material
* operational credentials
* telemetry
* control actions
* policy bundles

This separation is mandatory for Phase 1.

---

# Phase 1 Implementation Notes

For Phase 1, bootstrap should remain as simple as possible.

Do not add:

* bidirectional bootstrap messaging
* bootstrap publish acknowledgements from node
* secret exchange
* control commands
* remote procedure calls

Bootstrap must remain a one-way Core-to-node discovery mechanism.

