import asyncio
import json
import os
from pathlib import Path
from typing import Awaitable, Callable

from ai_node.persistence.local_llm_benchmark_store import DEFAULT_LOCAL_LLM_BENCHMARK_MODELS
from ai_node.time_utils import local_now_iso


CommandRunner = Callable[[list[str], dict[str, str]], Awaitable[dict]]


class LocalLLMBenchmarkRotationRunner:
    def __init__(
        self,
        *,
        worker,
        logger,
        model_config_path: str = "config/local-llm-models.json",
        state_path: str = ".run/local_llm_benchmark_rotation.json",
        control_script: str = "scripts/llamacpp-control.sh",
        model_ids: list[str] | None = None,
        batch_limit: int = 25,
        command_runner: CommandRunner | None = None,
    ) -> None:
        self._worker = worker
        self._logger = logger
        self._model_config_path = Path(model_config_path)
        self._state_path = Path(state_path)
        self._control_script = str(control_script or "scripts/llamacpp-control.sh")
        self._model_ids = [str(item).strip() for item in (model_ids or DEFAULT_LOCAL_LLM_BENCHMARK_MODELS) if str(item).strip()]
        self._batch_limit = max(int(batch_limit), 1)
        self._command_runner = command_runner or self._run_command
        self._state_path.parent.mkdir(parents=True, exist_ok=True)

    async def run_once(self) -> dict:
        model = self._next_model()
        switch_result = await self._load_model(model)
        worker_result = await self._worker.run_pending_for_model(
            model_id=str(model["id"]),
            limit=self._batch_limit,
        )
        result = {
            "model_id": str(model["id"]),
            "model_repo": model.get("repo"),
            "model_file": model.get("file"),
            "ctx_size": model.get("ctx_size"),
            "switched_at": local_now_iso(),
            "switch_result": switch_result,
            "worker_result": worker_result,
        }
        self._save_state(model_id=str(model["id"]), result=result)
        return result

    def _next_model(self) -> dict:
        models = self._load_models()
        state = self._load_state()
        previous_id = str(state.get("current_model_id") or "").strip()
        previous_index = next((idx for idx, item in enumerate(models) if str(item.get("id")) == previous_id), -1)
        return models[(previous_index + 1) % len(models)]

    def _load_models(self) -> list[dict]:
        payload = {}
        if self._model_config_path.exists():
            try:
                payload = json.loads(self._model_config_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
        configured = payload.get("models") if isinstance(payload, dict) else []
        models_by_id = {
            str(item.get("id") or "").strip(): dict(item)
            for item in configured
            if isinstance(item, dict) and str(item.get("id") or "").strip()
        }
        selected = [models_by_id[model_id] for model_id in self._model_ids if model_id in models_by_id]
        if selected:
            return selected
        fallback = [
            {"id": model_id, "repo": "", "file": "", "quantization": "", "ctx_size": 4096}
            for model_id in self._model_ids
        ]
        if not fallback:
            raise ValueError("local_llm_benchmark_rotation_models_required")
        return fallback

    def _load_state(self) -> dict:
        if not self._state_path.exists():
            return {}
        try:
            payload = json.loads(self._state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _save_state(self, *, model_id: str, result: dict) -> None:
        payload = {
            "schema_version": "1.0",
            "current_model_id": model_id,
            "updated_at": local_now_iso(),
            "last_result": result,
        }
        self._state_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    async def _load_model(self, model: dict) -> dict:
        env = dict(os.environ)
        model_id = str(model.get("id") or "").strip()
        repo = str(model.get("repo") or "").strip()
        quantization = str(model.get("quantization") or "").strip()
        if repo and quantization:
            env["LLAMACPP_MODEL_HF"] = f"{repo}:{quantization}"
        env["LLAMACPP_MODEL_ALIAS"] = model_id
        if model.get("ctx_size") is not None:
            env["LLAMACPP_CTX_SIZE"] = str(model.get("ctx_size"))
        command = [self._control_script, "ready"]
        result = await self._command_runner(command, env)
        return {
            "command": command,
            "returncode": int(result.get("returncode") or 0),
            "stdout": str(result.get("stdout") or "")[-2000:],
            "stderr": str(result.get("stderr") or "")[-2000:],
        }

    @staticmethod
    async def _run_command(command: list[str], env: dict[str, str]) -> dict:
        process = await asyncio.create_subprocess_exec(
            *command,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError((stderr or stdout).decode("utf-8", errors="replace").strip() or "local_model_load_failed")
        return {
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
        }
