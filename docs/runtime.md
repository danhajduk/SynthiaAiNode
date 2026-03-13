# Runtime

## Startup Behavior

- without trust state, the node starts from `unconfigured` and enters bootstrap onboarding when configured
- with valid trust state, startup resumes through `trusted -> capability_setup_pending`
- trusted resume may continue to operational when accepted capability, fresh governance, and operational MQTT readiness are already valid

## Reconnect And Retry Behavior

- bootstrap connection is monitored by a timeout guard
- capability and governance flows use explicit result classification for retryable versus rejected failures
- provider capability refresh runs on a background interval when enabled

## Registration And Trust Assumptions

- onboarding depends on bootstrap MQTT plus Core HTTP APIs
- trust state and node identity must remain internally consistent
- invalid trust or config files are ignored and logged as non-sensitive failures

## Health And Telemetry

- `GET /api/health` returns a simple backend health response
- `GET /api/node/status` exposes lifecycle, trusted runtime context, capability setup state, capability runtime state, and service status
- trusted status telemetry publishes over operational MQTT only

## Degraded Behavior

- temporary capability submission, governance sync, operational readiness, or telemetry failures can transition the node to `degraded`
- recovery is explicit through the control API and startup resume logic

## Shutdown Behavior

- bootstrap runner and timeout monitor are stopped when the backend exits
- provider background tasks are managed through the control app lifecycle
