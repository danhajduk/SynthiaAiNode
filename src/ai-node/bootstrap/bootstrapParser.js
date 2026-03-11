const REQUIRED_FIELDS = [
  "topic",
  "bootstrap_version",
  "core_id",
  "core_name",
  "core_version",
  "api_base",
  "mqtt_host",
  "mqtt_port",
  "onboarding_endpoints",
  "onboarding_mode",
  "emitted_at",
];

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function hasRequiredFields(payload) {
  return REQUIRED_FIELDS.every((key) => Object.hasOwn(payload, key));
}

function validateRegisterEndpoint(payload) {
  const register = payload.onboarding_endpoints?.register;
  return isNonEmptyString(register);
}

function normalizePayload(payload) {
  return {
    topic: payload.topic.trim(),
    bootstrap_version: Number(payload.bootstrap_version),
    core_id: payload.core_id.trim(),
    core_name: payload.core_name.trim(),
    core_version: payload.core_version.trim(),
    api_base: payload.api_base.trim(),
    mqtt_host: payload.mqtt_host.trim(),
    mqtt_port: Number(payload.mqtt_port),
    onboarding_endpoints: {
      register: payload.onboarding_endpoints.register.trim(),
    },
    onboarding_mode: payload.onboarding_mode.trim(),
    emitted_at: payload.emitted_at.trim(),
  };
}

export function buildRegistrationUrl(apiBase, registerPath) {
  const api = String(apiBase ?? "").trim();
  const path = String(registerPath ?? "").trim();

  if (!isNonEmptyString(api)) {
    throw new Error("api_base is required");
  }
  if (!isNonEmptyString(path)) {
    throw new Error("onboarding_endpoints.register is required");
  }

  const base = new URL(api.endsWith("/") ? api : `${api}/`);
  const pathWithoutLeadingSlash = path.startsWith("/") ? path.slice(1) : path;
  return new URL(pathWithoutLeadingSlash, base).toString();
}

export function parseBootstrapPayload(rawPayload) {
  try {
    const text =
      typeof rawPayload === "string"
        ? rawPayload
        : Buffer.isBuffer(rawPayload)
          ? rawPayload.toString("utf8")
          : String(rawPayload);

    return { ok: true, value: JSON.parse(text) };
  } catch {
    return { ok: false, error: "invalid_json" };
  }
}

export function validateBootstrapPayload(payload, options = {}) {
  const supportedVersions = options.supportedVersions ?? [1];
  const expectedTopic = options.expectedTopic ?? "synthia/bootstrap/core";

  if (!payload || typeof payload !== "object") {
    return { ok: false, error: "invalid_payload" };
  }
  if (!hasRequiredFields(payload)) {
    return { ok: false, error: "missing_required_fields" };
  }
  if (!validateRegisterEndpoint(payload)) {
    return { ok: false, error: "missing_register_endpoint" };
  }

  const normalized = normalizePayload(payload);
  if (normalized.topic !== expectedTopic) {
    return { ok: false, error: "invalid_topic" };
  }
  if (!supportedVersions.includes(normalized.bootstrap_version)) {
    return { ok: false, error: "unsupported_bootstrap_version" };
  }
  if (normalized.onboarding_mode !== "api") {
    return { ok: false, error: "unsupported_onboarding_mode" };
  }
  if (!isNonEmptyString(normalized.api_base)) {
    return { ok: false, error: "invalid_api_base" };
  }
  if (!isNonEmptyString(normalized.core_id) || !isNonEmptyString(normalized.core_name)) {
    return { ok: false, error: "invalid_core_identity" };
  }
  if (!isNonEmptyString(normalized.mqtt_host) || !Number.isFinite(normalized.mqtt_port)) {
    return { ok: false, error: "invalid_mqtt_target" };
  }
  if (!isNonEmptyString(normalized.emitted_at)) {
    return { ok: false, error: "invalid_emitted_at" };
  }

  try {
    return {
      ok: true,
      value: {
        ...normalized,
        registration_url: buildRegistrationUrl(
          normalized.api_base,
          normalized.onboarding_endpoints.register,
        ),
      },
    };
  } catch {
    return { ok: false, error: "invalid_registration_url" };
  }
}
