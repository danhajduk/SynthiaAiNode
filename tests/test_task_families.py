import unittest

from ai_node.capabilities.task_families import (
    CANONICAL_TASK_FAMILIES,
    create_declared_task_family_capabilities,
    validate_task_family_capabilities,
)


class TaskFamilyCapabilityTests(unittest.TestCase):
    def test_default_declared_task_families_match_canonical(self):
        declared = create_declared_task_family_capabilities()
        self.assertEqual(declared, list(CANONICAL_TASK_FAMILIES))

    def test_validate_rejects_unknown_task_family(self):
        is_valid, error = validate_task_family_capabilities(["text_classification", "audio_transcription"])
        self.assertFalse(is_valid)
        self.assertEqual(error, "unknown_task_family:audio_transcription")

    def test_create_rejects_unknown_task_family(self):
        with self.assertRaises(ValueError):
            create_declared_task_family_capabilities(["email_classification", "audio_transcription"])


if __name__ == "__main__":
    unittest.main()
