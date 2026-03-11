import asyncio
from dataclasses import dataclass
from typing import Optional

from ai_node.lifecycle.node_lifecycle import NodeLifecycle, NodeLifecycleState


@dataclass(frozen=True)
class PendingApprovalInfo:
    status: str
    approval_url: Optional[str]
    status_url: Optional[str]


def _require_pending_status(response: dict) -> None:
    if not isinstance(response, dict):
        raise ValueError("pending approval response must be an object")
    if response.get("status") != "pending_approval":
        raise ValueError("response status must be pending_approval")


class PendingApprovalWaiter:
    def __init__(
        self,
        *,
        lifecycle: NodeLifecycle,
        http_adapter,
        logger,
        poll_interval_seconds: float = 2.0,
        max_polls: int = 120,
    ) -> None:
        if lifecycle is None:
            raise ValueError("pending approval waiter requires lifecycle")
        if http_adapter is None or not hasattr(http_adapter, "get_json"):
            raise ValueError("pending approval waiter requires http_adapter.get_json")

        self._lifecycle = lifecycle
        self._http_adapter = http_adapter
        self._logger = logger
        self._poll_interval_seconds = poll_interval_seconds
        self._max_polls = max_polls

    def begin_pending_approval(self, registration_response: dict) -> PendingApprovalInfo:
        _require_pending_status(registration_response)
        info = PendingApprovalInfo(
            status="pending_approval",
            approval_url=registration_response.get("approval_url"),
            status_url=registration_response.get("status_url"),
        )
        self._lifecycle.transition_to(NodeLifecycleState.PENDING_APPROVAL)
        if hasattr(self._logger, "info"):
            self._logger.info(
                "[pending-approval] %s",
                {"approval_url": info.approval_url, "status_url": info.status_url},
            )
        return info

    async def wait_for_decision(self, approval_info: PendingApprovalInfo) -> dict:
        if not approval_info.status_url:
            raise ValueError("status_url is required for approval polling")

        for poll_index in range(1, self._max_polls + 1):
            response = await self._http_adapter.get_json(approval_info.status_url)
            status = response.get("status")
            if hasattr(self._logger, "info"):
                self._logger.info(
                    "[pending-approval-poll] %s",
                    {"poll_index": poll_index, "status": status},
                )

            if status == "pending_approval":
                await asyncio.sleep(self._poll_interval_seconds)
                continue
            if status in {"approved", "rejected"}:
                return response
            raise ValueError(f"unexpected approval status: {status}")

        raise TimeoutError("approval decision timed out while waiting")
