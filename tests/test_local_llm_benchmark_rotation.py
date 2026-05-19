import json
import logging
import tempfile
import unittest
from pathlib import Path

from ai_node.runtime.local_llm_benchmark_rotation import LocalLLMBenchmarkRotationRunner


class _FakeWorker:
    def __init__(self):
        self.calls = []

    async def run_pending_for_model(self, *, model_id: str, limit: int = 1):
        self.calls.append({"model_id": model_id, "limit": limit})
        return {"model_id": model_id, "processed": 2, "completed": 2, "failed": 0, "errors": []}


class LocalLLMBenchmarkRotationRunnerTests(unittest.IsolatedAsyncioTestCase):
    async def test_rotation_loads_next_model_and_runs_worker(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "models.json"
            config_path.write_text(
                json.dumps(
                    {
                        "models": [
                            {
                                "id": "qwen3-8b-q4_k_m",
                                "repo": "Qwen/Qwen3-8B-GGUF",
                                "quantization": "Q4_K_M",
                                "ctx_size": 4096,
                            },
                            {
                                "id": "gemma-3-12b-it-q4_k_m",
                                "repo": "bartowski/google_gemma-3-12b-it-GGUF",
                                "quantization": "Q4_K_M",
                                "ctx_size": 4096,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            commands = []

            async def fake_runner(command, env):
                commands.append({"command": command, "env": env})
                return {"returncode": 0, "stdout": "ready", "stderr": ""}

            worker = _FakeWorker()
            runner = LocalLLMBenchmarkRotationRunner(
                worker=worker,
                logger=logging.getLogger("local-llm-rotation-test"),
                model_config_path=str(config_path),
                state_path=str(Path(tmp) / "rotation.json"),
                control_script="scripts/llamacpp-control.sh",
                model_ids=["qwen3-8b-q4_k_m", "gemma-3-12b-it-q4_k_m"],
                batch_limit=7,
                command_runner=fake_runner,
            )

            first = await runner.run_once()
            second = await runner.run_once()

            self.assertEqual(first["model_id"], "qwen3-8b-q4_k_m")
            self.assertEqual(second["model_id"], "gemma-3-12b-it-q4_k_m")
            self.assertEqual(worker.calls, [{"model_id": "qwen3-8b-q4_k_m", "limit": 7}, {"model_id": "gemma-3-12b-it-q4_k_m", "limit": 7}])
            self.assertEqual(commands[0]["command"], ["scripts/llamacpp-control.sh", "ready"])
            self.assertEqual(commands[0]["env"]["LLAMACPP_MODEL_HF"], "Qwen/Qwen3-8B-GGUF:Q4_K_M")
            self.assertEqual(commands[1]["env"]["LLAMACPP_MODEL_ALIAS"], "gemma-3-12b-it-q4_k_m")
