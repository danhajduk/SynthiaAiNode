import unittest

from ai_node.runtime.feature_union import build_feature_union


class FeatureUnionTests(unittest.TestCase):
    def test_union_enables_feature_when_any_enabled_model_supports_it(self):
        payload = build_feature_union(
            model_feature_entries=[
                {"model_id": "gpt-5-mini", "features": {"chat": True, "reasoning": False}},
                {"model_id": "whisper-1", "features": {"speech_to_text": True, "chat": False}},
            ],
            enabled_models=["gpt-5-mini", "whisper-1"],
        )
        self.assertTrue(payload["chat"])
        self.assertTrue(payload["speech_to_text"])
        self.assertFalse(payload["reasoning"])

    def test_union_ignores_models_not_enabled(self):
        payload = build_feature_union(
            model_feature_entries=[
                {"model_id": "gpt-5-mini", "features": {"chat": True}},
                {"model_id": "whisper-1", "features": {"speech_to_text": True}},
            ],
            enabled_models=["gpt-5-mini"],
        )
        self.assertTrue(payload["chat"])
        self.assertFalse(payload["speech_to_text"])


if __name__ == "__main__":
    unittest.main()
