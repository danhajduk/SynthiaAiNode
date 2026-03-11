# Synthia AI Node — Trust State

## Purpose

After an AI Node is approved by Synthia Core, the node must store a **local trust state**.

This trust state allows the node to:

- authenticate with Core
- reconnect after reboot
- avoid repeating the bootstrap process
- operate as a trusted Synthia infrastructure node

Without stored trust state the node would need to repeat onboarding every time it starts.

---

# Trust State Storage Requirements

Trust state must be stored in **persistent local storage**.

The storage must survive:

- node restarts
- container restarts
- system reboots

Trust state must **not be lost between runs**.

---

# Required Stored Fields

The node must persist the following fields.

| Field | Description |
|------|-------------|
| node_id | unique system identifier issued by Core |
| node_name | human-readable node name |
| node_type | must be `ai-node` |
| paired_core_id | identifier of the Core instance |
| core_api_url | Core API base URL |
| node_token | authentication token issued by Core |
| mqtt_username | operational MQTT username |
| mqtt_password | operational MQTT password |
| baseline_policy | initial policy configuration |
| bootstrap_host | MQTT host used during discovery |
| registration_timestamp | time the node was approved |

---

# Example Stored Trust State

Example JSON representation:

```json
{
  "node_id": "node-ai-001",
  "node_name": "main-ai-node",
  "node_type": "ai-node",
  "paired_core_id": "core-main",
  "core_api_url": "http://192.168.1.50:9001",
  "node_token": "REDACTED",
  "mqtt_username": "main-ai-node",
  "mqtt_password": "REDACTED",
  "baseline_policy": {},
  "bootstrap_host": "192.168.1.10",
  "registration_timestamp": "2026-03-11T18:21:00Z"
}
````

The exact storage format may vary, but the required fields must be preserved.

---

# Sensitive Data Handling

The following fields are **sensitive credentials**:

* `node_token`
* `mqtt_password`

These values must never:

* be printed in logs
* appear in telemetry
* appear in error messages
* be exposed through debug APIs

Nodes should treat these values as secrets.

---

# Restart Behavior

When the AI Node starts, it must check whether a trust state exists.

## If trust state exists

The node must:

1. skip bootstrap discovery
2. load stored configuration
3. authenticate with Core using the stored token
4. reconnect to operational MQTT
5. transition lifecycle state to **operational**

Bootstrap must **not** be repeated.

---

## If trust state does not exist

The node must begin the onboarding process:

```
bootstrap discovery → registration → approval → trust activation
```

---

# Trust State Corruption

If the trust state is missing required fields or fails validation:

The node must treat it as **invalid**.

Behavior:

1. discard corrupted trust state
2. log error
3. restart onboarding process

Nodes must not attempt partial trust recovery.

---

# Trust State Location

The trust state file should be stored in a predictable location.

Example:

```
/var/lib/synthia/ai-node/trust.json
```

or

```
data/ai-node/trust.json
```

The exact location may vary depending on the runtime environment.

---

# Trust Reset

If the trust state file is deleted, the node becomes **untrusted** again.

The node must return to bootstrap discovery.

This allows operators to force a node to re-register.

---

# Security Principles

Trust state establishes the node as a **trusted system component**.

Therefore:

* trust state must persist securely
* secrets must never leak
* only approved nodes may obtain credentials

Trust state is the foundation of the node's identity within Synthia.

Loss of trust state means loss of identity.

