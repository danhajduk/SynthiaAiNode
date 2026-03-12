from datetime import datetime, timedelta, timezone
import unittest

from ai_node.governance.freshness import evaluate_governance_freshness


class GovernanceFreshnessTests(unittest.TestCase):
    def test_returns_unknown_when_missing_bundle(self):
        status = evaluate_governance_freshness(None)
        self.assertEqual(status["state"], "unknown")
        self.assertEqual(status["reason"], "missing_governance_bundle")

    def test_returns_fresh_when_within_max_stale_window(self):
        now = datetime(2026, 3, 11, 12, 0, tzinfo=timezone.utc)
        bundle = {
            "policy_version": "1.0",
            "issued_timestamp": "2026-03-11T11:00:00+00:00",
            "synced_at": (now - timedelta(seconds=300)).isoformat(),
            "refresh_expectations": {"recommended_interval_seconds": 900, "max_stale_seconds": 3600},
        }
        status = evaluate_governance_freshness(bundle, now=now)
        self.assertEqual(status["state"], "fresh")
        self.assertEqual(status["active_governance_version"], "1.0")

    def test_returns_stale_when_exceeding_max_stale_window(self):
        now = datetime(2026, 3, 11, 12, 0, tzinfo=timezone.utc)
        bundle = {
            "policy_version": "1.0",
            "issued_timestamp": "2026-03-11T10:00:00+00:00",
            "synced_at": (now - timedelta(seconds=5000)).isoformat(),
            "refresh_expectations": {"recommended_interval_seconds": 900, "max_stale_seconds": 3600},
        }
        status = evaluate_governance_freshness(bundle, now=now)
        self.assertEqual(status["state"], "stale")


if __name__ == "__main__":
    unittest.main()
