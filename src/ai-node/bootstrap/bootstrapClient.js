import { parseBootstrapPayload, validateBootstrapPayload } from "./bootstrapParser.js";
import { NODE_LIFECYCLE_STATES } from "../lifecycle/nodeLifecycle.js";

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function assertExactTopic(topic) {
  if (typeof topic !== "string" || topic.length === 0) {
    throw new Error("bootstrap topic is required");
  }
  if (topic.includes("#") || topic.includes("+")) {
    throw new Error("wildcard bootstrap topic is not allowed");
  }
}

export function createBootstrapClient(options) {
  if (!options || typeof options !== "object") {
    throw new Error("bootstrap client options are required");
  }

  const lifecycle = options.lifecycle;
  if (!lifecycle || typeof lifecycle.transitionTo !== "function") {
    throw new Error("bootstrap client requires lifecycle controller");
  }

  const logger = options.logger ?? console;
  const mqttAdapter = options.mqttAdapter;
  if (!mqttAdapter || typeof mqttAdapter.connect !== "function") {
    throw new Error("bootstrap client requires mqttAdapter.connect");
  }

  const retryConfig = {
    maxAttempts: options.maxAttempts ?? 5,
    baseDelayMs: options.baseDelayMs ?? 500,
    maxDelayMs: options.maxDelayMs ?? 5_000,
  };

  let client = null;
  let isRunning = false;

  async function connect(config, callbacks = {}) {
    assertExactTopic(config.topic);
    isRunning = true;
    let attempt = 0;

    while (isRunning && attempt < retryConfig.maxAttempts) {
      attempt += 1;
      lifecycle.transitionTo(NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTING, { attempt });

      try {
        client = await mqttAdapter.connect({
          host: config.bootstrapHost,
          port: config.port,
          username: undefined,
          password: undefined,
          clientId: config.nodeName,
          clean: true,
        });

        await client.subscribe(config.topic);
        lifecycle.transitionTo(NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTED, { attempt });
        logger.info?.("[bootstrap-connected]", {
          host: config.bootstrapHost,
          port: config.port,
          topic: config.topic,
        });

        client.onMessage((topic, rawPayload) => {
          if (topic !== config.topic) {
            return;
          }

          const parsed = parseBootstrapPayload(rawPayload);
          if (!parsed.ok) {
            logger.warn?.("[bootstrap-payload-ignored]", { reason: parsed.error });
            return;
          }

          const validated = validateBootstrapPayload(parsed.value, {
            expectedTopic: config.topic,
            supportedVersions: callbacks.supportedBootstrapVersions ?? [1],
          });
          if (!validated.ok) {
            logger.warn?.("[bootstrap-payload-ignored]", { reason: validated.error });
            return;
          }

          lifecycle.transitionTo(NODE_LIFECYCLE_STATES.CORE_DISCOVERED);
          callbacks.onCoreDiscovered?.(validated.value);
        });

        return {
          close: async () => {
            isRunning = false;
            await client?.close?.();
            client = null;
          },
        };
      } catch (error) {
        logger.warn?.("[bootstrap-connect-failed]", {
          attempt,
          maxAttempts: retryConfig.maxAttempts,
          message: error?.message ?? "unknown error",
        });

        if (attempt >= retryConfig.maxAttempts) {
          lifecycle.transitionTo(NODE_LIFECYCLE_STATES.DEGRADED, { stage: "bootstrap_connect" });
          throw new Error("bootstrap connection failed after bounded retries");
        }

        const nextDelayMs = Math.min(
          retryConfig.baseDelayMs * Math.pow(2, attempt - 1),
          retryConfig.maxDelayMs,
        );
        await delay(nextDelayMs);
      }
    }

    throw new Error("bootstrap client stopped");
  }

  return {
    connect,
    stop: async () => {
      isRunning = false;
      await client?.close?.();
      client = null;
    },
  };
}
