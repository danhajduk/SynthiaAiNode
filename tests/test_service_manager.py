import logging
import unittest
from unittest.mock import patch

from ai_node.runtime.service_manager import UserSystemdServiceManager


class _Completed:
    def __init__(self, stdout: str):
        self.stdout = stdout
        self.stderr = ""


class ServiceManagerTests(unittest.TestCase):
    def test_get_status_maps_systemctl_states(self):
        manager = UserSystemdServiceManager(logger=logging.getLogger("service-manager-test"))

        calls = {"count": 0}

        def _fake_run(cmd, check, capture_output, text, env=None):
            if cmd[:2] == ["docker", "inspect"]:
                return _Completed("0\n")
            if cmd[:3] == ["systemctl", "--user", "show"]:
                return _Completed("MainPID=0\n")
            self.assertEqual(cmd[:3], ["systemctl", "--user", "is-active"])
            calls["count"] += 1
            return _Completed("active\n" if calls["count"] == 1 else "failed\n")

        with patch("subprocess.run", side_effect=_fake_run):
            payload = manager.get_status()
        self.assertEqual(payload["backend"]["state"], "running")
        self.assertEqual(payload["frontend"]["state"], "failed")
        self.assertEqual(payload["local_llm"]["service_id"], "local_llm")
        self.assertEqual(payload["node"], "degraded")

    def test_restart_node_restarts_both_units(self):
        manager = UserSystemdServiceManager(logger=logging.getLogger("service-manager-test"))
        invoked = []

        def _fake_popen(cmd, **_kwargs):
            invoked.append(cmd)

        with patch("subprocess.Popen", side_effect=_fake_popen):
            result = manager.restart(target="node")
        self.assertEqual(result["target"], "node")
        restart_calls = [cmd for cmd in invoked if cmd[2] == "restart"]
        self.assertEqual(len(restart_calls), 2)

    def test_get_status_treats_activating_as_running(self):
        manager = UserSystemdServiceManager(logger=logging.getLogger("service-manager-test"))

        def _fake_run(cmd, check, capture_output, text, env=None):
            if cmd[:2] == ["docker", "inspect"]:
                return _Completed("0\n")
            if cmd[:3] == ["systemctl", "--user", "show"]:
                return _Completed("MainPID=0\n")
            self.assertEqual(cmd[:3], ["systemctl", "--user", "is-active"])
            return _Completed("activating\n")

        with patch("subprocess.run", side_effect=_fake_run):
            payload = manager.get_status()
        self.assertEqual(payload["backend"]["state"], "running")
        self.assertEqual(payload["frontend"]["state"], "running")
        self.assertEqual(payload["node"], "running")

    def test_schedule_restart_launches_detached_restart_command(self):
        manager = UserSystemdServiceManager(logger=logging.getLogger("service-manager-test"))

        with patch("subprocess.Popen") as fake_popen:
            result = manager.schedule_restart(target="backend", delay_seconds=10)

        self.assertEqual(result["target"], "backend")
        self.assertEqual(result["result"], "scheduled")
        self.assertEqual(result["delay_seconds"], 10)
        command = fake_popen.call_args.args[0]
        self.assertEqual(command[:2], ["bash", "-lc"])
        self.assertIn("sleep 10;", command[2])
        self.assertIn("systemctl --user restart synthia-ai-node-backend.service", command[2])

    def test_local_llm_status_reports_container_pid_cpu_and_memory(self):
        manager = UserSystemdServiceManager(logger=logging.getLogger("service-manager-test"))

        def _fake_run(cmd, check, capture_output, text, env=None):
            self.assertEqual(cmd[:3], ["docker", "inspect", "--format"])
            self.assertEqual(cmd[-1], "hexe-ai-node-llamacpp")
            return _Completed("4242\n")

        with (
            patch("os.path.exists", return_value=True),
            patch("subprocess.run", side_effect=_fake_run),
            patch.object(manager, "_read_cpu_total", side_effect=[1000.0, 1100.0]),
            patch.object(manager, "_read_process_cpu", side_effect=[50.0, 75.0]),
            patch.object(manager, "_read_mem_total", return_value=1000.0),
            patch.object(manager, "_read_process_rss", return_value=125.0),
        ):
            first_payload = manager._local_llm_status()
            second_payload = manager._local_llm_status()

        self.assertEqual(first_payload["state"], "running")
        self.assertEqual(first_payload["pid"], 4242)
        self.assertIsNone(first_payload["cpu_percent"])
        self.assertEqual(first_payload["mem_percent"], 12.5)
        self.assertEqual(first_payload["container_name"], "hexe-ai-node-llamacpp")
        self.assertEqual(second_payload["cpu_percent"], 25.0)


if __name__ == "__main__":
    unittest.main()
