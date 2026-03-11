from ai_node.security.redaction import redact_dict


class OnboardingDiagnosticsLogger:
    def __init__(self, logger) -> None:
        self._logger = logger

    def state_transition(self, payload: dict) -> None:
        if hasattr(self._logger, "info"):
            self._logger.info("[diag.state_transition] %s", redact_dict(payload))

    def bootstrap_connect(self, payload: dict) -> None:
        if hasattr(self._logger, "info"):
            self._logger.info("[diag.bootstrap_connect] %s", redact_dict(payload))

    def bootstrap_disconnect(self, payload: dict) -> None:
        if hasattr(self._logger, "warning"):
            self._logger.warning("[diag.bootstrap_disconnect] %s", redact_dict(payload))

    def payload_validation(self, payload: dict) -> None:
        if hasattr(self._logger, "info"):
            self._logger.info("[diag.payload_validation] %s", redact_dict(payload))

    def registration_attempt(self, payload: dict) -> None:
        if hasattr(self._logger, "info"):
            self._logger.info("[diag.registration_attempt] %s", redact_dict(payload))

    def approval_wait(self, payload: dict) -> None:
        if hasattr(self._logger, "info"):
            self._logger.info("[diag.approval_wait] %s", redact_dict(payload))

    def trust_persistence(self, payload: dict) -> None:
        if hasattr(self._logger, "info"):
            self._logger.info("[diag.trust_persistence] %s", redact_dict(payload))
