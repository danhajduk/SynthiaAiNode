import unittest

from ai_node.diagnostics.onboarding_logger import OnboardingDiagnosticsLogger


class _CaptureLogger:
    def __init__(self):
        self.entries = []

    def info(self, msg, payload):
        self.entries.append((msg, payload))

    def warning(self, msg, payload):
        self.entries.append((msg, payload))


class OnboardingLoggerTests(unittest.TestCase):
    def test_diagnostics_logger_redacts_sensitive_fields(self):
        capture = _CaptureLogger()
        diag = OnboardingDiagnosticsLogger(capture)
        diag.trust_persistence(
            {
                "action": "load",
                "node_trust_token": "secret-token",
                "operational_mqtt_token": "mqtt-secret",
            }
        )
        _, payload = capture.entries[-1]
        self.assertEqual(payload["node_trust_token"], "***REDACTED***")
        self.assertEqual(payload["operational_mqtt_token"], "***REDACTED***")


if __name__ == "__main__":
    unittest.main()
