import re
from typing import Optional, Tuple


TASK_CLASSIFICATION = "task.classification"
TASK_SUMMARIZATION = "task.summarization"

CANONICAL_TASK_FAMILIES = (
    TASK_CLASSIFICATION,
    TASK_SUMMARIZATION,
)

_TASK_FAMILY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]{1,127}$")


def _normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            normalized.append(item.strip())
    return sorted(set(normalized))


def create_declared_task_family_capabilities(task_families: list[str] | None = None) -> list[str]:
    declared = _normalize_string_list(task_families) if isinstance(task_families, list) else list(CANONICAL_TASK_FAMILIES)
    is_valid, error = validate_task_family_capabilities(declared)
    if not is_valid:
        raise ValueError(f"invalid task family declaration: {error}")
    return declared


def validate_task_family_capabilities(task_families: object) -> Tuple[bool, Optional[str]]:
    if not isinstance(task_families, list):
        return False, "invalid_task_families"
    normalized = _normalize_string_list(task_families)
    if not normalized:
        return True, None
    invalid = [family for family in normalized if not _TASK_FAMILY_ID_RE.match(family)]
    if invalid:
        return False, f"invalid_task_family:{invalid[0]}"
    return True, None
