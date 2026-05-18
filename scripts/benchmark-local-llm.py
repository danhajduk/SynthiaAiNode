#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import socket
import time
from pathlib import Path


PROMPTS = [
    {
        "name": "classification",
        "temperature": 0.0,
        "messages": [
            {"role": "system", "content": "Return only JSON with label, confidence, and reasoning."},
            {"role": "user", "content": "Classify this request: Please summarize this invoice and flag any overdue payment."},
        ],
    },
    {
        "name": "summarization",
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": "Summarize in three bullets: The node must run local LLM inference over sockets, expose health, and compare local versus OpenAI latency."},
        ],
    },
    {
        "name": "reasoning",
        "temperature": 0.4,
        "messages": [
            {"role": "user", "content": "A task can run locally or on OpenAI. Explain which provider to use when privacy matters and latency is acceptable."},
        ],
    },
]


def _uds_post_json(socket_path: str, path: str, payload: dict, *, timeout_s: float) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    request = (
        f"POST {path} HTTP/1.1\r\n"
        "Host: llamacpp\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode("utf-8") + body
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(timeout_s)
        client.connect(socket_path)
        client.sendall(request)
        chunks: list[bytes] = []
        while True:
            chunk = client.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    raw = b"".join(chunks)
    head, _, response_body = raw.partition(b"\r\n\r\n")
    status_code = int(head.split(maxsplit=2)[1])
    return status_code, json.loads(response_body.decode("utf-8")) if response_body else {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark the local llama.cpp runtime over its Unix socket.")
    parser.add_argument("--socket-path", default="/run/hexe/ai-node/llamacpp.sock")
    parser.add_argument("--model", default="qwen3-8b-q4_k_m")
    parser.add_argument("--output", default=".run/local_llm_benchmark.json")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--timeout-s", type=float, default=180.0)
    args = parser.parse_args()

    results = []
    for prompt in PROMPTS:
        request = {
            "model": args.model,
            "messages": prompt["messages"],
            "temperature": prompt["temperature"],
            "max_tokens": args.max_tokens,
            "stream": False,
        }
        started = time.perf_counter()
        try:
            status_code, payload = _uds_post_json(args.socket_path, "/v1/chat/completions", request, timeout_s=args.timeout_s)
            elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
            usage = payload.get("usage") if isinstance(payload, dict) else {}
            choices = payload.get("choices") if isinstance(payload, dict) else []
            first = choices[0] if isinstance(choices, list) and choices else {}
            message = first.get("message") if isinstance(first, dict) else {}
            completion_tokens = int((usage or {}).get("completion_tokens") or 0)
            results.append(
                {
                    "name": prompt["name"],
                    "status": "completed" if status_code < 400 else "failed",
                    "http_status": status_code,
                    "elapsed_ms": elapsed_ms,
                    "completion_tokens": completion_tokens,
                    "tokens_per_second": round((completion_tokens / elapsed_ms) * 1000.0, 3) if elapsed_ms > 0 and completion_tokens else None,
                    "output_text": str(message.get("content") or "")[:2000],
                    "usage": usage,
                }
            )
        except Exception as exc:
            results.append({"name": prompt["name"], "status": "failed", "error": str(exc)})
    output = {
        "schema_version": "1.0",
        "model": args.model,
        "socket_path": args.socket_path,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if all(item.get("status") == "completed" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
