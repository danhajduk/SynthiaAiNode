import logging
import unittest

from ai_node.telemetry.status_emitter import StatusEmitter


class _FakeSink:
    def __init__(self):
        self.events = []

    async def emit(self, payload: dict):
        self.events.append(payload)


class StatusEmitterTests(unittest.IsolatedAsyncioTestCase):
    async def test_emits_allowed_phase1_status_over_trusted_channel(self):
        sink = _FakeSink()
        emitter = StatusEmitter(sink=sink, logger=logging.getLogger("status-emitter-test"), channel="trusted")

        event = await emitter.emit("trusted", {"node_id": "node-ai-001"})
        self.assertEqual(event.status, "trusted")
        self.assertEqual(sink.events[-1]["channel"], "trusted")
        self.assertEqual(sink.events[-1]["status"], "trusted")

    async def test_rejects_bootstrap_channel_usage(self):
        sink = _FakeSink()
        with self.assertRaisesRegex(ValueError, "must not be routed over bootstrap"):
            StatusEmitter(sink=sink, logger=logging.getLogger("status-emitter-test"), channel="bootstrap")

    async def test_rejects_unsupported_status(self):
        sink = _FakeSink()
        emitter = StatusEmitter(sink=sink, logger=logging.getLogger("status-emitter-test"), channel="internal")
        with self.assertRaisesRegex(ValueError, "unsupported phase1 status event"):
            await emitter.emit("ai_workload_started")


if __name__ == "__main__":
    unittest.main()
