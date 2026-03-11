import threading
import time

from ai_node.lifecycle.node_lifecycle import NodeLifecycle, NodeLifecycleState


class BootstrapConnectTimeoutMonitor:
    def __init__(
        self,
        *,
        lifecycle: NodeLifecycle,
        logger,
        timeout_seconds: float = 30.0,
        poll_interval_seconds: float = 0.5,
    ) -> None:
        self._lifecycle = lifecycle
        self._logger = logger
        self._timeout_seconds = timeout_seconds
        self._poll_interval_seconds = poll_interval_seconds
        self._deadline = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None

    def on_transition(self, transition: dict) -> None:
        to_state = transition.get("to")
        with self._lock:
            if to_state == NodeLifecycleState.BOOTSTRAP_CONNECTING:
                self._deadline = time.monotonic() + self._timeout_seconds
                if hasattr(self._logger, "info"):
                    self._logger.info(
                        "[bootstrap-timeout-monitor] armed for %ss",
                        self._timeout_seconds,
                    )
            else:
                self._deadline = None

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            deadline = None
            with self._lock:
                deadline = self._deadline

            if deadline is not None and time.monotonic() >= deadline:
                if self._lifecycle.get_state() == NodeLifecycleState.BOOTSTRAP_CONNECTING:
                    try:
                        self._lifecycle.transition_to(
                            NodeLifecycleState.UNCONFIGURED,
                            {
                                "reason": "bootstrap_connect_timeout",
                                "timeout_seconds": self._timeout_seconds,
                            },
                        )
                        if hasattr(self._logger, "warning"):
                            self._logger.warning(
                                "[bootstrap-timeout-monitor] bootstrap_connecting timeout reached (%ss)",
                                self._timeout_seconds,
                            )
                    except Exception as exc:
                        if hasattr(self._logger, "warning"):
                            self._logger.warning(
                                "[bootstrap-timeout-monitor] timeout transition failed: %s",
                                str(exc),
                            )
                with self._lock:
                    self._deadline = None

            self._stop_event.wait(self._poll_interval_seconds)
