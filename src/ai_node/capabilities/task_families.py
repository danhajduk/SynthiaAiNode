from typing import Optional, Tuple


TEXT_CLASSIFICATION = "text_classification"
EMAIL_CLASSIFICATION = "email_classification"
IMAGE_CLASSIFICATION = "image_classification"
IMAGE_GENERATION = "image_generation"

CANONICAL_TASK_FAMILIES = (
    TEXT_CLASSIFICATION,
    EMAIL_CLASSIFICATION,
    IMAGE_CLASSIFICATION,
    IMAGE_GENERATION,
)


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
    unknown = [family for family in normalized if family not in CANONICAL_TASK_FAMILIES]
    if unknown:
        return False, f"unknown_task_family:{unknown[0]}"
    return True, None
