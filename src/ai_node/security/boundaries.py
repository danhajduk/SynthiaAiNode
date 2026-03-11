FORBIDDEN_BOOTSTRAP_TRUST_FIELDS = {
    "node_trust_token",
    "operational_mqtt_token",
    "operational_mqtt_identity",
    "initial_baseline_policy",
}


def enforce_bootstrap_security_boundary(payload: object):
    if not isinstance(payload, dict):
        return False, "invalid_payload"

    forbidden_present = sorted(FORBIDDEN_BOOTSTRAP_TRUST_FIELDS.intersection(payload.keys()))
    if forbidden_present:
        return False, f"forbidden_bootstrap_fields:{','.join(forbidden_present)}"
    return True, None


def require_approval_before_trust_activation(decision_response: object):
    if not isinstance(decision_response, dict):
        raise ValueError("approval decision response must be an object")
    if decision_response.get("status") != "approved":
        raise ValueError("approval is required before trust activation")
    return decision_response
