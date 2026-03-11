from dataclasses import dataclass
from typing import Optional

from ai_node.lifecycle.node_lifecycle import NodeLifecycle, NodeLifecycleState
from ai_node.trust.trust_store import TrustStateStore


@dataclass(frozen=True)
class StartupDecision:
    mode: str
    trust_state: Optional[dict]
    reason: str


class TrustedStartupManager:
    def __init__(self, *, trust_store: TrustStateStore, lifecycle: NodeLifecycle, logger) -> None:
        self._trust_store = trust_store
        self._lifecycle = lifecycle
        self._logger = logger

    def resolve_startup_path(self) -> StartupDecision:
        trusted_state = self._trust_store.load()
        if trusted_state is not None:
            self._lifecycle.transition_to(
                NodeLifecycleState.TRUSTED,
                {"startup_mode": "trusted_resume"},
            )
            self._lifecycle.transition_to(
                NodeLifecycleState.CAPABILITY_SETUP_PENDING,
                {"startup_mode": "trusted_resume"},
            )
            if hasattr(self._logger, "info"):
                self._logger.info(
                    "[startup-path] %s",
                    {"mode": "trusted_resume", "state": NodeLifecycleState.CAPABILITY_SETUP_PENDING.value},
                )
            return StartupDecision(
                mode="trusted_resume",
                trust_state=trusted_state,
                reason="valid_trust_state_found",
            )

        self._lifecycle.transition_to(
            NodeLifecycleState.BOOTSTRAP_CONNECTING,
            {"startup_mode": "bootstrap_onboarding"},
        )
        if hasattr(self._logger, "info"):
            self._logger.info(
                "[startup-path] %s",
                {"mode": "bootstrap_onboarding", "state": NodeLifecycleState.BOOTSTRAP_CONNECTING.value},
            )
        return StartupDecision(
            mode="bootstrap_onboarding",
            trust_state=None,
            reason="trust_state_missing_or_invalid",
        )
