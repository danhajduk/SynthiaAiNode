# Synthia AI Node — Lifecycle States

## Purpose

The AI Node operates using a defined lifecycle state machine.

Lifecycle states allow the node to:

- track onboarding progress
- manage bootstrap behavior
- handle registration
- respond to failures
- recover from restarts

A deterministic lifecycle is required so that the node behaves predictably.

---

# Lifecycle States

The node must implement the following states.

| State | Description |
|------|-------------|
| unconfigured | node has no configuration or trust state |
| bootstrap_connecting | node attempting connection to bootstrap MQTT |
| bootstrap_connected | node connected to bootstrap broker |
| core_discovered | node received valid bootstrap message |
| registration_pending | node sent registration request |
| pending_approval | waiting for operator approval |
| trusted | node approved but not yet fully operational |
| operational | node fully connected and trusted |
| degraded | node temporarily lost connection to Core |

---

# State Diagram

```

unconfigured
│
▼
bootstrap_connecting
│
▼
bootstrap_connected
│
▼
core_discovered
│
▼
registration_pending
│
▼
pending_approval
│
▼
trusted
│
▼
operational

```

---

# Detailed State Descriptions

## unconfigured

The node has:

- no stored trust state
- no Core identity
- no credentials

The node must begin bootstrap discovery.

---

## bootstrap_connecting

The node is attempting to connect to the bootstrap MQTT broker.

Connection parameters:

```

port: 1884
auth: anonymous

```

Failure handling:

- retry with backoff

---

## bootstrap_connected

The node successfully connected to the bootstrap broker.

The node must:

- subscribe to `synthia/bootstrap`
- wait for a valid payload

---

## core_discovered

A valid bootstrap payload was received.

The node now knows:

- Core API location
- registration endpoint
- protocol version

The node must begin registration.

---

## registration_pending

The node has submitted a registration request to Core.

The node is waiting for a response.

Possible responses:

- pending approval
- rejected
- immediate approval (rare)

---

## pending_approval

The node is waiting for operator approval.

Behavior:

- log approval URL
- poll status endpoint
- wait for approval response

The node must not repeatedly resend registration requests.

---

## trusted

The node has been approved by Core.

The node has received:

- node_id
- node_token
- operational MQTT credentials
- baseline policy

The node must now store trust state locally.

---

## operational

The node is fully trusted and connected.

The node may now:

- authenticate with Core
- connect to operational MQTT
- begin participating in the Synthia system

AI execution is **not enabled yet in Phase 1**.

---

## degraded

This state occurs if the node temporarily loses communication with Core.

Examples:

- Core API unavailable
- MQTT connection lost

Behavior:

- retry connection
- remain trusted
- return to operational when connectivity restored

---

# Restart Behavior

When the node starts, it must determine its initial state.

## Trust state exists

Node must start in:

```

trusted → operational

```

Bootstrap must be skipped.

---

## Trust state missing

Node must start in:

```

unconfigured

```

and begin bootstrap discovery.

---

# Logging Requirements

Each lifecycle state transition must be logged.

Example log entries:

```

[STATE] bootstrap_connecting
[STATE] bootstrap_connected
[STATE] core_discovered
[STATE] registration_pending
[STATE] pending_approval
[STATE] trusted
[STATE] operational

```

Logs help operators diagnose onboarding problems.

---

# Phase 1 Scope

For Phase 1, lifecycle states are used only for onboarding and connectivity.

Future phases will extend lifecycle handling for:

- provider failures
- AI runtime availability
- policy enforcement states
- resource exhaustion
