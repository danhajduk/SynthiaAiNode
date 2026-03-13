# Operations

## Logs

- backend log file default: `logs/backend.log`
- runtime logs include onboarding, trust persistence, capability activation, telemetry, provider refresh, and service-control events

## Health Checks

- `curl http://127.0.0.1:9002/api/health`
- `curl http://127.0.0.1:9002/api/node/status`
- `curl http://127.0.0.1:9002/api/governance/status`
- `curl http://127.0.0.1:9002/debug/providers`
- `curl http://127.0.0.1:9002/debug/providers/models`
- `curl http://127.0.0.1:9002/debug/providers/metrics`

## Common Failure Modes

- invalid or missing trust state prevents trusted resume
- bootstrap broker unavailable or wrong host prevents onboarding
- Core API errors block capability declaration or governance sync
- missing operational MQTT credentials blocks trusted status publication
- missing `OPENAI_API_KEY` limits live OpenAI provider discovery
- user systemd bus access issues make service status appear `unknown`

## Recovery Steps

1. Check `logs/backend.log` for the most recent lifecycle or telemetry error.
2. Inspect `GET /api/node/status` for lifecycle state, blocking reasons, and trusted runtime context.
3. Verify `.run/trust_state.json` and `.run/node_identity.json` are present and internally consistent.
4. Re-run provider or governance refresh through the control API if the node is trusted but stale.
5. Restart backend or full node services with the service controls when process state is stuck.

## First Things To Inspect During Incident Response

- current lifecycle state
- trust-state validity
- Core API reachability
- operational MQTT reachability
- provider refresh/debug endpoints
- service manager status for backend and frontend
