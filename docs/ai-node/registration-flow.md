# Synthia AI Node — Registration Flow

## Purpose

After discovering Synthia Core through the bootstrap mechanism, an AI Node must register itself with Core.

Registration establishes:

- node identity
- operator approval workflow
- trust activation
- issuance of node credentials
- baseline policy delivery

Registration occurs **exclusively through the Core HTTP API**.

MQTT must **not** be used for registration transactions.

---

# Registration Sequence

The node must follow this sequence:

```

AI Node
│
│ bootstrap discovery
▼
Receive Core bootstrap payload
│
│ send registration request
▼
Core creates pending node
│
│ operator approval required
▼
Operator approves node
│
│ trust activation response
▼
Node stores trust state
│
▼
Node becomes trusted

```

---

# Registration Endpoint

The node sends a registration request to the Core API.

```

POST /api/nodes/register

```

The endpoint URL is constructed from the bootstrap payload:

```

{core_api_url}{registration_endpoint}

```

Example:

```

[http://192.168.1.50:9001/api/nodes/register](http://192.168.1.50:9001/api/nodes/register)

````

---

# Registration Request Payload

The node must send the following payload.

Example:

```json
{
  "node_name": "main-ai-node",
  "node_type": "ai-node",
  "node_version": "0.1.0",
  "protocol_version": 1,
  "hostname": "ai-server"
}
````

Fields:

| Field            | Description                      |
| ---------------- | -------------------------------- |
| node_name        | human readable node identifier   |
| node_type        | must be `"ai-node"`              |
| node_version     | node software version            |
| protocol_version | bootstrap protocol compatibility |
| hostname         | optional host identifier         |

---

# Core Registration Handling

When Core receives the registration request it must:

1. create a **pending node record**
2. store metadata
3. require **operator approval**

The node must not become trusted automatically.

---

# Pending Approval Response

Core should respond with a **pending approval state**.

Example:

```json
{
  "status": "pending_approval",
  "approval_url": "http://core.local/ui/nodes/pending"
}
```

Fields:

| Field        | Description                    |
| ------------ | ------------------------------ |
| status       | registration state             |
| approval_url | location for operator approval |

---

# Node Behavior During Pending Approval

When a node receives `pending_approval`, it must:

* log the approval URL
* remain in **pending approval state**
* periodically check approval status

The node must **not retry registration repeatedly**.

Instead it should poll a status endpoint or wait for approval confirmation.

---

# Operator Approval

An operator must approve the node in the Core UI.

Example UI information:

```
Node requesting access

Name: main-ai-node
Type: ai-node
Host: ai-server
Version: 0.1.0

[Approve]   [Reject]
```

Approval is a manual security control.

---

# Approval Response

When approved, Core returns the trust activation payload.

Example:

```json
{
  "status": "approved",
  "node_id": "node-ai-001",
  "node_token": "REDACTED_TOKEN",
  "baseline_policy": {},
  "mqtt_credentials": {
    "username": "main-ai-node",
    "password": "REDACTED"
  }
}
```

Fields:

| Field            | Description                   |
| ---------------- | ----------------------------- |
| node_id          | unique system node identifier |
| node_token       | authentication token          |
| baseline_policy  | initial policy configuration  |
| mqtt_credentials | operational MQTT credentials  |

---

# Rejection Response

If the operator rejects the node, Core should return:

```json
{
  "status": "rejected"
}
```

The node must terminate the onboarding process.

---

# Node Responsibilities After Approval

Once approved, the node must:

1. store trust data locally
2. transition lifecycle state to **trusted**
3. connect using operational credentials
4. begin trusted communication with Core

The node must never discard or expose credentials.

---

# Retry and Failure Handling

Registration should include basic failure handling.

Examples:

### Core unavailable

Node should retry registration after delay.

### Invalid payload

Node should log error and stop registration attempt.

### Rejection

Node should terminate onboarding.

---

# Security Principles

Registration must follow these rules:

* registration is **API only**
* approval is **operator controlled**
* secrets are delivered **only after approval**
* nodes start with **zero trust**

Bootstrap alone must never grant trust.

Trust is granted **only after successful registration and approval**.

