export const BOOTSTRAP_DEFAULTS = Object.freeze({
  port: 1884,
  anonymous: true,
  topic: "synthia/bootstrap/core",
});

function requireNonEmptyString(value, name) {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`${name} is required`);
  }
  return value.trim();
}

export function createBootstrapConfig(input) {
  if (!input || typeof input !== "object") {
    throw new Error("bootstrap input is required");
  }

  const bootstrapHost = requireNonEmptyString(input.bootstrapHost, "bootstrapHost");
  const nodeName = requireNonEmptyString(input.nodeName, "nodeName");

  return Object.freeze({
    bootstrapHost,
    nodeName,
    port: BOOTSTRAP_DEFAULTS.port,
    anonymous: BOOTSTRAP_DEFAULTS.anonymous,
    topic: BOOTSTRAP_DEFAULTS.topic,
  });
}
