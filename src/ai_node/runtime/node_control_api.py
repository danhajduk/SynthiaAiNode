import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ai_node.config.bootstrap_config import create_bootstrap_config
from ai_node.lifecycle.node_lifecycle import NodeLifecycle, NodeLifecycleState


class NodeControlState:
    def __init__(self, *, lifecycle: NodeLifecycle, config_path: str, logger) -> None:
        self._lifecycle = lifecycle
        self._config_path = Path(config_path)
        self._logger = logger
        self._lock = threading.Lock()
        self._bootstrap_config = None
        self._load_existing_config()

    def _load_existing_config(self) -> None:
        if not self._config_path.exists():
            return
        try:
            payload = json.loads(self._config_path.read_text(encoding="utf-8"))
            self._bootstrap_config = create_bootstrap_config(payload)
            if self._lifecycle.get_state() == NodeLifecycleState.UNCONFIGURED:
                self._lifecycle.transition_to(
                    NodeLifecycleState.BOOTSTRAP_CONNECTING,
                    {"source": "persisted_bootstrap_config"},
                )
        except Exception:
            if hasattr(self._logger, "warning"):
                self._logger.warning(
                    "[node-control] invalid persisted bootstrap config ignored: %s", self._config_path
                )

    def status_payload(self) -> dict:
        state = self._lifecycle.get_state()
        return {
            "status": state.value,
            "bootstrap_configured": self._bootstrap_config is not None,
        }

    def initiate_onboarding(self, *, mqtt_host: str, node_name: str) -> dict:
        with self._lock:
            if self._lifecycle.get_state() != NodeLifecycleState.UNCONFIGURED:
                raise ValueError("node is not in unconfigured state")

            config = create_bootstrap_config(
                {
                    "bootstrap_host": mqtt_host,
                    "node_name": node_name,
                }
            )
            self._bootstrap_config = config
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            self._config_path.write_text(
                json.dumps(
                    {
                        "bootstrap_host": config.bootstrap_host,
                        "node_name": config.node_name,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            self._lifecycle.transition_to(
                NodeLifecycleState.BOOTSTRAP_CONNECTING,
                {"source": "setup_ui"},
            )
            return self.status_payload()


class NodeControlApiServer:
    def __init__(self, *, host: str, port: int, state: NodeControlState, logger) -> None:
        self._host = host
        self._port = port
        self._state = state
        self._logger = logger
        self._httpd = None
        self._thread = None

    def start(self) -> None:
        state = self._state
        logger = self._logger

        class Handler(BaseHTTPRequestHandler):
            def _send_json(self, status: int, payload: dict) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
                self.end_headers()
                self.wfile.write(body)

            def do_OPTIONS(self):
                self._send_json(HTTPStatus.OK, {"ok": True})

            def do_GET(self):
                if self.path == "/api/node/status":
                    self._send_json(HTTPStatus.OK, state.status_payload())
                    return
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

            def do_POST(self):
                if self.path != "/api/onboarding/initiate":
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                    return
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(length)
                    payload = json.loads(raw.decode("utf-8"))
                    result = state.initiate_onboarding(
                        mqtt_host=str(payload.get("mqtt_host", "")),
                        node_name=str(payload.get("node_name", "")),
                    )
                    self._send_json(HTTPStatus.OK, result)
                except ValueError as exc:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                except Exception:
                    self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "internal_error"})

            def log_message(self, fmt, *args):
                if hasattr(logger, "info"):
                    logger.info("[node-control-api] " + fmt, *args)

        self._httpd = ThreadingHTTPServer((self._host, self._port), Handler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        if hasattr(self._logger, "info"):
            self._logger.info("[node-control-api] listening on %s:%s", self._host, self._port)

    def stop(self) -> None:
        if self._httpd is None:
            return
        self._httpd.shutdown()
        self._httpd.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)
