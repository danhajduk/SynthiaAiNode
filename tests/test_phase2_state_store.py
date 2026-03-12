import logging
import tempfile
import unittest
from pathlib import Path

from ai_node.persistence.phase2_state_store import Phase2StateStore, validate_phase2_state


def _sample_payload() -> dict:
    return {
        "schema_version": "1.0",
        "enabled_provider_selection": {"providers": {"enabled": ["openai"]}},
        "accepted_capability": {"accepted_declaration_version": "1.0"},
        "active_governance": {"policy_version": "1.0"},
        "timestamps": {
            "capability_declaration_timestamp": "2026-03-11T00:00:00Z",
            "governance_sync_timestamp": "2026-03-11T00:01:00Z",
        },
    }


class Phase2StateStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger("phase2-state-store-test")

    def test_validate_accepts_sample_payload(self):
        is_valid, error = validate_phase2_state(_sample_payload())
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_store_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "phase2_state.json"
            store = Phase2StateStore(path=str(path), logger=self.logger)
            payload = _sample_payload()
            store.save(payload)
            loaded = store.load()
            self.assertEqual(loaded, payload)

    def test_load_migrates_legacy_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "phase2_state.json"
            path.write_text(
                """{
  "provider_selection": {"providers": {"enabled": ["openai"]}},
  "capability_state": {"accepted_declaration_version": "1.0"},
  "governance_state": {"policy_version": "1.0"},
  "timestamps": {}
}""",
                encoding="utf-8",
            )
            store = Phase2StateStore(path=str(path), logger=self.logger)
            loaded = store.load()
            self.assertEqual(loaded["schema_version"], "1.0")
            self.assertIn("enabled_provider_selection", loaded)


if __name__ == "__main__":
    unittest.main()
