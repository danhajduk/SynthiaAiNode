import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from ai_node.providers.adapters.openai_adapter import OpenAIProviderAdapter
from ai_node.providers.openai_catalog import OpenAIPricingCatalogService
from ai_node.providers.models import UnifiedExecutionRequest


TEST_OPENAI_CREDENTIAL = "placeholder-openai-credential"


class OpenAIAdapterCostTests(unittest.TestCase):
    def test_estimate_cost_uses_current_gpt_54_rates(self):
        with tempfile.TemporaryDirectory() as tmp:
            adapter = OpenAIProviderAdapter(
                api_key=TEST_OPENAI_CREDENTIAL,
                pricing_catalog_service=OpenAIPricingCatalogService(
                    logger=None,
                    catalog_path=str(Path(tmp) / "provider_model_pricing.json"),
                    manual_config_path=str(Path(tmp) / "openai-pricing.yaml"),
                ),
            )

            cost = adapter.estimate_cost(
                model_id="gpt-5.4",
                prompt_tokens=169,
                completion_tokens=127,
            )

            self.assertIsNotNone(cost)
            self.assertAlmostEqual(cost, 0.0023275, places=10)

    def test_estimate_cost_uses_current_gpt_54_mini_rates(self):
        with tempfile.TemporaryDirectory() as tmp:
            adapter = OpenAIProviderAdapter(
                api_key=TEST_OPENAI_CREDENTIAL,
                pricing_catalog_service=OpenAIPricingCatalogService(
                    logger=None,
                    catalog_path=str(Path(tmp) / "provider_model_pricing.json"),
                    manual_config_path=str(Path(tmp) / "openai-pricing.yaml"),
                ),
            )

            cost = adapter.estimate_cost(
                model_id="gpt-5.4-mini",
                prompt_tokens=250,
                cached_input_tokens=100,
                completion_tokens=50,
            )

            self.assertIsNotNone(cost)
            self.assertAlmostEqual(cost, 0.000345, places=10)

    def test_estimate_cost_uses_current_gpt_54_nano_rates(self):
        with tempfile.TemporaryDirectory() as tmp:
            adapter = OpenAIProviderAdapter(
                api_key=TEST_OPENAI_CREDENTIAL,
                pricing_catalog_service=OpenAIPricingCatalogService(
                    logger=None,
                    catalog_path=str(Path(tmp) / "provider_model_pricing.json"),
                    manual_config_path=str(Path(tmp) / "openai-pricing.yaml"),
                ),
            )

            cost = adapter.estimate_cost(
                model_id="gpt-5.4-nano",
                prompt_tokens=353,
                completion_tokens=191,
            )

            self.assertIsNotNone(cost)
            self.assertAlmostEqual(cost, 0.00030935, places=10)

    def test_estimate_cost_uses_cached_input_rate_when_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            adapter = OpenAIProviderAdapter(
                api_key=TEST_OPENAI_CREDENTIAL,
                pricing_catalog_service=OpenAIPricingCatalogService(
                    logger=None,
                    catalog_path=str(Path(tmp) / "provider_model_pricing.json"),
                    manual_config_path=str(Path(tmp) / "openai-pricing.yaml"),
                ),
            )

            cost = adapter.estimate_cost(
                model_id="gpt-5.4",
                prompt_tokens=250,
                cached_input_tokens=100,
                completion_tokens=50,
            )

            self.assertIsNotNone(cost)
            self.assertAlmostEqual(cost, 0.00115, places=10)


class _FakeResponse:
    def __init__(self, payload: dict, *, status_code: int = 200):
        self.status_code = status_code
        self.headers = {"content-type": "application/json"}
        self._payload = payload

    def json(self):
        return self._payload


class _FakeAsyncClient:
    def __init__(self, *, capture: dict, payload: dict, status_code: int = 200, **_kwargs):
        self._capture = capture
        self._payload = payload
        self._status_code = status_code

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, *, headers=None, json=None):
        self._capture["url"] = url
        self._capture["headers"] = headers
        self._capture["json"] = json
        return _FakeResponse(self._payload, status_code=self._status_code)


class OpenAIAdapterExecutionTests(unittest.IsolatedAsyncioTestCase):
    async def test_classification_requests_enable_json_response_format(self):
        capture: dict = {}
        response_payload = {
            "id": "resp-123",
            "choices": [{"message": {"content": "{\"label\":\"marketing\"}"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        adapter = OpenAIProviderAdapter(api_key=TEST_OPENAI_CREDENTIAL)
        request = UnifiedExecutionRequest(
            task_family="task.classification",
            prompt="Classify this email",
            requested_model="gpt-5.4-nano",
        )

        with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
            response = await adapter.execute_prompt(request)

        self.assertEqual(response.output_text, "{\"label\":\"marketing\"}")
        self.assertEqual(capture["json"]["response_format"], {"type": "json_object"})

    async def test_structured_output_schema_uses_json_schema_response_format(self):
        capture: dict = {}
        response_payload = {
            "id": "resp-789",
            "choices": [{"message": {"content": "{\"primary_label\":\"ORDER\"}"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        adapter = OpenAIProviderAdapter(api_key=TEST_OPENAI_CREDENTIAL)
        request = UnifiedExecutionRequest(
            task_family="task.classification",
            prompt="Analyze this email",
            requested_model="gpt-5.4-mini",
            metadata={
                "prompt_id": "prompt.email.action_decision",
                "prompt_version": "v1.4",
                "structured_output_schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "primary_label": {"type": "string"},
                    },
                    "required": ["primary_label"],
                },
            },
        )

        with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
            response = await adapter.execute_prompt(request)

        self.assertEqual(response.output_text, "{\"primary_label\":\"ORDER\"}")
        self.assertEqual(capture["json"]["response_format"]["type"], "json_schema")
        self.assertEqual(capture["json"]["response_format"]["json_schema"]["strict"], True)
        self.assertEqual(
            capture["json"]["response_format"]["json_schema"]["schema"]["required"],
            ["primary_label"],
        )
        self.assertAlmostEqual(response.estimated_cost or 0.0, 0.00003, places=12)

    async def test_structured_output_schema_normalizes_optional_object_properties_for_openai(self):
        capture: dict = {}
        response_payload = {
            "id": "resp-790",
            "choices": [{"message": {"content": "{\"match\":{\"vendor_identity\":null}}"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        adapter = OpenAIProviderAdapter(api_key=TEST_OPENAI_CREDENTIAL)
        request = UnifiedExecutionRequest(
            task_family="task.summarization.text",
            prompt="Build template",
            requested_model="gpt-5.4-mini",
            metadata={
                "structured_output_schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "match": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "vendor_identity": {"type": "string"},
                            },
                        }
                    },
                    "required": ["match"],
                },
            },
        )

        with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
            await adapter.execute_prompt(request)

        normalized_schema = capture["json"]["response_format"]["json_schema"]["schema"]
        self.assertEqual(normalized_schema["properties"]["match"]["required"], ["vendor_identity"])
        self.assertEqual(
            normalized_schema["properties"]["match"]["properties"]["vendor_identity"]["type"],
            ["string", "null"],
        )

    async def test_structured_output_schema_drops_one_of_for_openai_compatibility(self):
        capture: dict = {}
        response_payload = {
            "id": "resp-791",
            "choices": [{"message": {"content": "{\"extract\":{}}"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        adapter = OpenAIProviderAdapter(api_key=TEST_OPENAI_CREDENTIAL)
        request = UnifiedExecutionRequest(
            task_family="task.summarization.text",
            prompt="Build template",
            requested_model="gpt-5.4-mini",
            metadata={
                "structured_output_schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "extract": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "method": {"type": "string"},
                                    "pattern": {"type": "string"},
                                },
                                "required": ["method"],
                                "oneOf": [
                                    {"required": ["method", "pattern"]},
                                ],
                            },
                        }
                    },
                    "required": ["extract"],
                },
            },
        )

        with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
            await adapter.execute_prompt(request)

        additional_properties = capture["json"]["response_format"]["json_schema"]["schema"]["properties"]["extract"]["additionalProperties"]
        self.assertNotIn("oneOf", additional_properties)

    async def test_structured_output_schema_adds_additional_properties_false_to_bare_objects(self):
        capture: dict = {}
        response_payload = {
            "id": "resp-792",
            "choices": [{"message": {"content": "{\"post_process\":{}}"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        adapter = OpenAIProviderAdapter(api_key=TEST_OPENAI_CREDENTIAL)
        request = UnifiedExecutionRequest(
            task_family="task.summarization.text",
            prompt="Build template",
            requested_model="gpt-5.4-mini",
            metadata={
                "structured_output_schema": {
                    "type": "object",
                    "properties": {
                        "post_process": {"type": "object"},
                    },
                    "required": ["post_process"],
                }
            },
        )

        with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
            await adapter.execute_prompt(request)

        post_process = capture["json"]["response_format"]["json_schema"]["schema"]["properties"]["post_process"]
        self.assertFalse(post_process["additionalProperties"])

    async def test_non_classification_requests_do_not_force_json_response_format(self):
        capture: dict = {}
        response_payload = {
            "id": "resp-456",
            "choices": [{"message": {"content": "summary text"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        adapter = OpenAIProviderAdapter(api_key=TEST_OPENAI_CREDENTIAL)
        request = UnifiedExecutionRequest(
            task_family="task.summarization.text",
            prompt="Summarize this email",
            requested_model="gpt-5.4-nano",
        )

        with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
            response = await adapter.execute_prompt(request)

        self.assertEqual(response.output_text, "summary text")
        self.assertNotIn("response_format", capture["json"])

    async def test_image_generation_uses_images_api_with_gpt_image_model(self):
        capture: dict = {}
        response_payload = {
            "created": 1770000000,
            "data": [{"b64_json": "aW1hZ2U=", "revised_prompt": "A clean product image"}],
            "usage": {"input_tokens": 12, "output_tokens": 2, "total_tokens": 14},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        with tempfile.TemporaryDirectory() as tmp:
            adapter = OpenAIProviderAdapter(
                api_key=TEST_OPENAI_CREDENTIAL,
                pricing_catalog_service=OpenAIPricingCatalogService(
                    logger=None,
                    catalog_path="providers/openai/provider_model_pricing.json",
                    manual_config_path=str(Path(tmp) / "openai-pricing.yaml"),
                ),
            )
            request = UnifiedExecutionRequest(
                task_family="task.image_generation",
                prompt="Make a clean product image",
                requested_model="gpt-image-1-mini",
                metadata={"size": "1024x1024", "quality": "medium"},
            )

            with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
                response = await adapter.execute_prompt(request)

        self.assertEqual(capture["url"], "https://api.openai.com/v1/images/generations")
        self.assertEqual(capture["json"]["model"], "gpt-image-1-mini")
        self.assertEqual(capture["json"]["prompt"], "Make a clean product image")
        self.assertEqual(capture["json"]["size"], "1024x1024")
        self.assertEqual(capture["json"]["quality"], "medium")
        self.assertNotIn("messages", capture["json"])
        output = json.loads(response.output_text)
        self.assertEqual(output["images"][0]["b64_json"], "aW1hZ2U=")
        self.assertEqual(response.model_id, "gpt-image-1-mini")
        self.assertEqual(response.usage.prompt_tokens, 12)
        self.assertIsNotNone(response.estimated_cost)
        self.assertAlmostEqual(response.estimated_cost, 0.000046, places=10)

    async def test_debug_image_generation_overwrites_latest_prompt_file(self):
        capture: dict = {}
        response_payload = {
            "created": 1770000000,
            "data": [{"b64_json": "aW1hZ2U="}],
            "usage": {"input_tokens": 12, "output_tokens": 2, "total_tokens": 14},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        with tempfile.TemporaryDirectory() as tmp:
            debug_log_path = Path(tmp) / "openai_debug.jsonl"
            latest_prompt_path = Path(tmp) / "openai_last_image_prompt.txt"
            adapter = OpenAIProviderAdapter(
                api_key=TEST_OPENAI_CREDENTIAL,
                debug_aopenai=True,
                debug_aopenai_log_path=str(debug_log_path),
            )

            with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
                await adapter.execute_prompt(
                    UnifiedExecutionRequest(
                        task_family="task.image_generation",
                        prompt="First weather prompt",
                        requested_model="gpt-image-1-mini",
                        metadata={
                            "prompt_id": "prompt.weather.condition_background",
                            "prompt_version": "v4",
                            "size": "1536x1024",
                            "output_format": "png",
                        },
                    )
                )
                await adapter.execute_prompt(
                    UnifiedExecutionRequest(
                        task_family="task.image_generation",
                        prompt="Second weather prompt",
                        requested_model="gpt-image-1-mini",
                        metadata={
                            "prompt_id": "prompt.weather.condition_background",
                            "prompt_version": "v4",
                            "size": "1536x1024",
                            "output_format": "png",
                        },
                    )
                )

            self.assertTrue(debug_log_path.exists())
            self.assertEqual(len(debug_log_path.read_text(encoding="utf-8").splitlines()), 2)
            latest_prompt = latest_prompt_path.read_text(encoding="utf-8")
            self.assertIn("prompt_id: prompt.weather.condition_background", latest_prompt)
            self.assertIn("model: gpt-image-1-mini", latest_prompt)
            self.assertIn("size: 1536x1024", latest_prompt)
            self.assertIn("output_format: png", latest_prompt)
            self.assertIn("Second weather prompt", latest_prompt)
            self.assertNotIn("First weather prompt", latest_prompt)

    async def test_structured_extraction_does_not_send_json_schema_response_format(self):
        capture: dict = {}
        response_payload = {
            "id": "resp-793",
            "choices": [{"message": {"content": "{\"template_id\":\"demo\"}"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        adapter = OpenAIProviderAdapter(api_key=TEST_OPENAI_CREDENTIAL)
        request = UnifiedExecutionRequest(
            task_family="task.structured_extraction",
            prompt="Build template",
            requested_model="gpt-5.4-mini",
            metadata={
                "structured_output_schema": {
                    "type": "object",
                    "properties": {"template_id": {"type": "string"}},
                    "required": ["template_id"],
                }
            },
        )

        with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
            await adapter.execute_prompt(request)

        self.assertNotIn("response_format", capture["json"])

    async def test_http_error_uses_provider_message_field(self):
        capture: dict = {}
        response_payload = {
            "error": {
                "message": "Invalid schema for response_format 'order_template': schema must include additionalProperties: false",
                "type": "invalid_request_error",
                "param": "response_format",
                "code": None,
            }
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, status_code=400, **kwargs)

        adapter = OpenAIProviderAdapter(api_key=TEST_OPENAI_CREDENTIAL)
        request = UnifiedExecutionRequest(
            task_family="task.structured_extraction",
            prompt="Build template",
            requested_model="gpt-5.4-mini",
            metadata={
                "structured_output_schema": {
                    "type": "object",
                    "properties": {"template_id": {"type": "string"}},
                    "required": ["template_id"],
                }
            },
        )

        with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
            with self.assertRaisesRegex(RuntimeError, "Invalid schema for response_format"):
                await adapter.execute_prompt(request)

    async def test_debug_aopenai_writes_full_request_and_response_to_separate_log(self):
        capture: dict = {}
        response_payload = {
            "id": "resp-debug",
            "choices": [{"message": {"content": "{\"ok\":true}"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        def _client_factory(*args, **kwargs):
            return _FakeAsyncClient(capture=capture, payload=response_payload, **kwargs)

        with tempfile.TemporaryDirectory() as tmp:
            debug_log_path = Path(tmp) / "openai_debug.jsonl"
            adapter = OpenAIProviderAdapter(
                api_key=TEST_OPENAI_CREDENTIAL,
                debug_aopenai=True,
                debug_aopenai_log_path=str(debug_log_path),
            )
            request = UnifiedExecutionRequest(
                task_family="task.classification",
                prompt="Analyze this email",
                requested_model="gpt-5.4-mini",
                metadata={"prompt_id": "prompt.email.action_decision"},
            )

            with patch("ai_node.providers.adapters.openai_adapter.httpx.AsyncClient", side_effect=_client_factory):
                response = await adapter.execute_prompt(request)

            self.assertEqual(response.output_text, "{\"ok\":true}")
            self.assertTrue(debug_log_path.exists())
            records = [json.loads(line) for line in debug_log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["prompt_id"], "prompt.email.action_decision")
            self.assertEqual(records[0]["request_payload"]["model"], "gpt-5.4-mini")
            self.assertEqual(records[0]["response_payload"]["id"], "resp-debug")
            self.assertEqual(records[0]["request_headers"]["Authorization"], "***REDACTED***")


if __name__ == "__main__":
    unittest.main()
