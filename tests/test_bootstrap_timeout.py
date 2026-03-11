import logging
import time
import unittest

from ai_node.lifecycle.node_lifecycle import NodeLifecycle, NodeLifecycleState
from ai_node.runtime.bootstrap_timeout import BootstrapConnectTimeoutMonitor


class BootstrapTimeoutMonitorTests(unittest.TestCase):
    def test_timeout_moves_bootstrap_connecting_to_unconfigured(self):
        lifecycle = NodeLifecycle(logger=logging.getLogger("bootstrap-timeout-test"))
        monitor = BootstrapConnectTimeoutMonitor(
            lifecycle=lifecycle,
            logger=logging.getLogger("bootstrap-timeout-test"),
            timeout_seconds=0.05,
            poll_interval_seconds=0.01,
        )
        monitor.start()
        try:
            lifecycle.transition_to(NodeLifecycleState.BOOTSTRAP_CONNECTING)
            monitor.on_transition({"to": NodeLifecycleState.BOOTSTRAP_CONNECTING})
            time.sleep(0.12)
            self.assertEqual(lifecycle.get_state(), NodeLifecycleState.UNCONFIGURED)
        finally:
            monitor.stop()

    def test_transition_out_of_bootstrap_connecting_cancels_timeout(self):
        lifecycle = NodeLifecycle(logger=logging.getLogger("bootstrap-timeout-test"))
        monitor = BootstrapConnectTimeoutMonitor(
            lifecycle=lifecycle,
            logger=logging.getLogger("bootstrap-timeout-test"),
            timeout_seconds=0.08,
            poll_interval_seconds=0.01,
        )
        monitor.start()
        try:
            lifecycle.transition_to(NodeLifecycleState.BOOTSTRAP_CONNECTING)
            monitor.on_transition({"to": NodeLifecycleState.BOOTSTRAP_CONNECTING})
            lifecycle.transition_to(NodeLifecycleState.BOOTSTRAP_CONNECTED)
            monitor.on_transition({"to": NodeLifecycleState.BOOTSTRAP_CONNECTED})
            time.sleep(0.12)
            self.assertEqual(lifecycle.get_state(), NodeLifecycleState.BOOTSTRAP_CONNECTED)
        finally:
            monitor.stop()


if __name__ == "__main__":
    unittest.main()
