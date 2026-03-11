import unittest

from ai_node.capabilities.environment_hints import collect_environment_hints, validate_environment_hints


class EnvironmentHintsTests(unittest.TestCase):
    def test_collect_environment_hints_returns_expected_shape(self):
        hints = collect_environment_hints(
            hostname="node-a",
            os_platform="linux-test",
            total_memory_bytes=8 * 1024 * 1024 * 1024,
            gpu_present=False,
        )
        self.assertEqual(hints["hostname"], "node-a")
        self.assertEqual(hints["os_platform"], "linux-test")
        self.assertEqual(hints["memory_class"], "medium")
        self.assertFalse(hints["gpu_present"])

    def test_validate_rejects_invalid_memory_class(self):
        is_valid, error = validate_environment_hints(
            {
                "hostname": "node-a",
                "os_platform": "linux",
                "memory_class": "ultra",
                "gpu_present": False,
            }
        )
        self.assertFalse(is_valid)
        self.assertEqual(error, "invalid_memory_class")

    def test_validate_rejects_missing_hostname(self):
        is_valid, error = validate_environment_hints(
            {
                "hostname": "",
                "os_platform": "linux",
                "memory_class": "standard",
                "gpu_present": False,
            }
        )
        self.assertFalse(is_valid)
        self.assertEqual(error, "invalid_hostname")


if __name__ == "__main__":
    unittest.main()
