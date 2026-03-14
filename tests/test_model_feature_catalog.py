import logging
import tempfile
import unittest
from pathlib import Path

from ai_node.providers.model_feature_catalog import ProviderModelFeatureCatalogStore


class ModelFeatureCatalogStoreTests(unittest.TestCase):
    def test_save_entries_persists_expected_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "providers" / "openai" / "provider_model_features.json"
            store = ProviderModelFeatureCatalogStore(
                path=str(path),
                logger=logging.getLogger("model-feature-catalog-test"),
            )
            snapshot = store.save_entries(
                provider="openai",
                classification_model="gpt-5-nano",
                classified_at="2026-03-13T20:55:00Z",
                entries=[
                    {
                        "model_id": "gpt-5-mini",
                        "features": {"chat": True, "reasoning": True},
                    },
                    {
                        "model_id": "whisper-1",
                        "features": {"audio_input": True, "speech_to_text": True},
                    },
                ],
            )

            self.assertTrue(path.exists())
            self.assertEqual(len(snapshot.entries), 2)
            self.assertEqual(snapshot.entries[0].model_id, "gpt-5-mini")
            self.assertEqual(snapshot.entries[0].provider, "openai")
            self.assertEqual(snapshot.entries[0].classification_model, "gpt-5-nano")
            self.assertEqual(snapshot.entries[0].classified_at, "2026-03-13T20:55:00Z")
            self.assertTrue(snapshot.entries[0].features["chat"])

    def test_payload_round_trip_uses_provider_model_features_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "providers" / "openai" / "provider_model_features.json"
            store = ProviderModelFeatureCatalogStore(
                path=str(path),
                logger=logging.getLogger("model-feature-catalog-test"),
            )
            store.save_entries(
                provider="openai",
                classification_model="gpt-5-mini",
                entries=[{"model_id": "gpt-5-mini", "features": {"chat": True}}],
            )
            payload = store.payload()
            self.assertEqual(payload["source"], "provider_model_features")
            self.assertEqual(payload["entries"][0]["model_id"], "gpt-5-mini")
            self.assertEqual(payload["entries"][0]["provider"], "openai")


if __name__ == "__main__":
    unittest.main()
