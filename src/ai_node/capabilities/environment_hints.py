import os
import platform
import socket
from typing import Optional, Tuple


VALID_MEMORY_CLASSES = ("low", "medium", "standard", "high", "unknown")


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _classify_memory(total_bytes: int | None) -> str:
    if not isinstance(total_bytes, int) or total_bytes <= 0:
        return "unknown"
    gib = total_bytes / (1024**3)
    if gib <= 4:
        return "low"
    if gib <= 8:
        return "medium"
    if gib <= 16:
        return "standard"
    return "high"


def _detect_total_memory_bytes() -> int | None:
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        if pages > 0 and page_size > 0:
            return int(pages * page_size)
    except Exception:
        return None
    return None


def _detect_gpu_present() -> bool:
    # Lightweight heuristic; phase 2 does not require hardware inventory depth.
    if os.path.exists("/dev/nvidia0"):
        return True
    if os.path.exists("/dev/dri/renderD128"):
        return True
    return False


def collect_environment_hints(
    *,
    hostname: str | None = None,
    os_platform: str | None = None,
    total_memory_bytes: int | None = None,
    gpu_present: bool | None = None,
) -> dict:
    resolved_total_memory = total_memory_bytes if isinstance(total_memory_bytes, int) else _detect_total_memory_bytes()
    hints = {
        "hostname": str(hostname or socket.gethostname()).strip(),
        "os_platform": str(os_platform or platform.platform()).strip(),
        "memory_class": _classify_memory(resolved_total_memory),
        "gpu_present": bool(_detect_gpu_present() if gpu_present is None else gpu_present),
    }
    is_valid, error = validate_environment_hints(hints)
    if not is_valid:
        raise ValueError(f"invalid environment hints: {error}")
    return hints


def validate_environment_hints(data: object) -> Tuple[bool, Optional[str]]:
    if not isinstance(data, dict):
        return False, "invalid_environment_hints"
    if not _is_non_empty_string(data.get("hostname")):
        return False, "invalid_hostname"
    if not _is_non_empty_string(data.get("os_platform")):
        return False, "invalid_os_platform"
    memory_class = str(data.get("memory_class") or "").strip()
    if memory_class not in VALID_MEMORY_CLASSES:
        return False, "invalid_memory_class"
    if not isinstance(data.get("gpu_present"), bool):
        return False, "invalid_gpu_present"
    return True, None
