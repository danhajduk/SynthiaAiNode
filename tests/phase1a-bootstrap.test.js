import test from "node:test";
import assert from "node:assert/strict";

import { createBootstrapConfig } from "../src/ai-node/config/bootstrapConfig.js";
import { createNodeLifecycle, NODE_LIFECYCLE_STATES } from "../src/ai-node/lifecycle/nodeLifecycle.js";
import {
  buildRegistrationUrl,
  parseBootstrapPayload,
  validateBootstrapPayload,
} from "../src/ai-node/bootstrap/bootstrapParser.js";
import { createBootstrapClient } from "../src/ai-node/bootstrap/bootstrapClient.js";

test("createBootstrapConfig enforces required inputs and fixed defaults", () => {
  const config = createBootstrapConfig({
    bootstrapHost: "10.0.0.100",
    nodeName: "node-a",
  });

  assert.equal(config.bootstrapHost, "10.0.0.100");
  assert.equal(config.nodeName, "node-a");
  assert.equal(config.port, 1884);
  assert.equal(config.anonymous, true);
  assert.equal(config.topic, "synthia/bootstrap/core");
  assert.throws(() => createBootstrapConfig({ bootstrapHost: "", nodeName: "x" }), /required/);
});

test("node lifecycle supports canonical states and transition checks", () => {
  const lifecycle = createNodeLifecycle({ logger: { info: () => {} } });
  lifecycle.transitionTo(NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTING);
  lifecycle.transitionTo(NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTED);
  lifecycle.transitionTo(NODE_LIFECYCLE_STATES.CORE_DISCOVERED);

  assert.equal(lifecycle.getState(), NODE_LIFECYCLE_STATES.CORE_DISCOVERED);
  assert.equal(lifecycle.canTransitionTo(NODE_LIFECYCLE_STATES.REGISTRATION_PENDING), true);
  assert.throws(
    () => lifecycle.transitionTo(NODE_LIFECYCLE_STATES.TRUSTED),
    /invalid state transition/,
  );
});

test("bootstrap payload parser and validator enforce canonical contract", () => {
  const sample = {
    topic: "synthia/bootstrap/core",
    bootstrap_version: 1,
    core_id: "core-main",
    core_name: "Synthia Core",
    core_version: "1.0.0",
    api_base: "http://192.168.1.50:9001",
    mqtt_host: "192.168.1.50",
    mqtt_port: 1884,
    onboarding_endpoints: {
      register: "/api/nodes/register",
    },
    onboarding_mode: "api",
    emitted_at: "2026-03-11T18:21:00Z",
  };

  const parsed = parseBootstrapPayload(JSON.stringify(sample));
  assert.equal(parsed.ok, true);
  const validated = validateBootstrapPayload(parsed.value);
  assert.equal(validated.ok, true);
  assert.equal(
    validated.value.registration_url,
    "http://192.168.1.50:9001/api/nodes/register",
  );

  const invalid = validateBootstrapPayload({
    ...sample,
    onboarding_mode: "mqtt",
  });
  assert.equal(invalid.ok, false);
  assert.equal(invalid.error, "unsupported_onboarding_mode");
});

test("buildRegistrationUrl composes base and endpoint safely", () => {
  assert.equal(
    buildRegistrationUrl("http://core.local:9001", "/api/nodes/register"),
    "http://core.local:9001/api/nodes/register",
  );
  assert.equal(
    buildRegistrationUrl("http://core.local:9001/api/", "nodes/register"),
    "http://core.local:9001/api/nodes/register",
  );
});

test("bootstrap client subscribes exact topic and discovers valid payload", async () => {
  const lifecycle = createNodeLifecycle({ logger: { info: () => {} } });

  let messageHandler = null;
  const fakeClient = {
    subscribe: async (topic) => {
      assert.equal(topic, "synthia/bootstrap/core");
    },
    onMessage: (handler) => {
      messageHandler = handler;
    },
    close: async () => {},
  };

  const client = createBootstrapClient({
    lifecycle,
    logger: { info: () => {}, warn: () => {} },
    mqttAdapter: {
      connect: async () => fakeClient,
    },
  });

  const discovered = [];
  await client.connect(
    createBootstrapConfig({
      bootstrapHost: "10.0.0.100",
      nodeName: "node-a",
    }),
    {
      onCoreDiscovered: (payload) => discovered.push(payload),
    },
  );

  const payload = {
    topic: "synthia/bootstrap/core",
    bootstrap_version: 1,
    core_id: "core-main",
    core_name: "Synthia Core",
    core_version: "1.0.0",
    api_base: "http://192.168.1.50:9001",
    mqtt_host: "192.168.1.50",
    mqtt_port: 1884,
    onboarding_endpoints: { register: "/api/nodes/register" },
    onboarding_mode: "api",
    emitted_at: "2026-03-11T18:21:00Z",
  };

  messageHandler("synthia/bootstrap/core", JSON.stringify(payload));
  assert.equal(discovered.length, 1);
  assert.equal(lifecycle.getState(), NODE_LIFECYCLE_STATES.CORE_DISCOVERED);
});
