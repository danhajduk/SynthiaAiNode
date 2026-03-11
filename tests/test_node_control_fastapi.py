import logging
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from ai_node.lifecycle.node_lifecycle import NodeLifecycle
from ai_node.runtime.node_control_api import NodeControlState, create_node_control_app


class NodeControlFastApiTests(unittest.TestCase):
    def test_status_and_onboarding_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            lifecycle = NodeLifecycle(logger=logging.getLogger("node-control-fastapi-test"))
            state = NodeControlState(
                lifecycle=lifecycle,
                config_path=str(Path(tmp) / "bootstrap_config.json"),
                logger=logging.getLogger("node-control-fastapi-test"),
            )
            app = create_node_control_app(state=state, logger=logging.getLogger("node-control-fastapi-test"))
            client = TestClient(app)

            status_response = client.get("/api/node/status")
            self.assertEqual(status_response.status_code, 200)
            self.assertEqual(status_response.json()["status"], "unconfigured")

            initiate_response = client.post(
                "/api/onboarding/initiate",
                json={"mqtt_host": "10.0.0.100", "node_name": "main-ai-node"},
            )
            self.assertEqual(initiate_response.status_code, 200)
            self.assertEqual(initiate_response.json()["status"], "bootstrap_connecting")


if __name__ == "__main__":
    unittest.main()
