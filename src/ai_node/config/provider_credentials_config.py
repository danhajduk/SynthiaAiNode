import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple


PROVIDER_CREDENTIALS_SCHEMA_VERSION = "1.0"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        item_value = _normalize_string(item)
        if item_value and item_value not in normalized:
            normalized.append(item_value)
    return normalized


def _mask_secret(value: object) -> str | None:
    normalized = _normalize_string(value)
    if normalized is None:
        return None
    if len(normalized) <= 4:
        return "*" * len(normalized)
    return f"{'*' * max(len(normalized) - 4, 4)}{normalized[-4:]}"


def _normalize_provider_payload(payload: object) -> dict:
    if not isinstance(payload, dict):
        return {}
    return {
        "api_key": _normalize_string(payload.get("api_key")),
        "admin_key": _normalize_string(payload.get("admin_key")),
        "user_identifier": _normalize_string(payload.get("user_identifier")),
        "default_model_id": _normalize_string(payload.get("default_model_id")),
        "selected_model_ids": _normalize_string_list(payload.get("selected_model_ids")),
        "updated_at": _normalize_string(payload.get("updated_at")) or _iso_now(),
    }


def validate_provider_credentials(payload: object) -> Tuple[bool, Optional[str]]:
    if not isinstance(payload, dict):
        return False, "invalid_provider_credentials_object"
    if _normalize_string(payload.get("schema_version")) != PROVIDER_CREDENTIALS_SCHEMA_VERSION:
        return False, "invalid_schema_version"
    providers = payload.get("providers")
    if not isinstance(providers, dict):
        return False, "invalid_providers"
    for provider_name, provider_payload in providers.items():
        if not _normalize_string(provider_name):
            return False, "invalid_provider_name"
        if not isinstance(provider_payload, dict):
            return False, "invalid_provider_payload"
        updated_at = _normalize_string(provider_payload.get("updated_at"))
        if updated_at is None:
            return False, "missing_provider_updated_at"
    return True, None


def create_provider_credentials_payload(*, openai: dict | None = None) -> dict:
    providers: dict[str, dict] = {}
    normalized_openai = _normalize_provider_payload(openai)
    if normalized_openai:
        providers["openai"] = normalized_openai
    payload = {
        "schema_version": PROVIDER_CREDENTIALS_SCHEMA_VERSION,
        "providers": providers,
    }
    is_valid, error = validate_provider_credentials(payload)
    if not is_valid:
        raise ValueError(f"invalid provider credentials payload: {error}")
    return payload


def summarize_provider_credentials(payload: dict | None) -> dict:
    if not isinstance(payload, dict):
        return {"configured": False, "providers": {}}
    providers = payload.get("providers")
    if not isinstance(providers, dict):
        return {"configured": False, "providers": {}}
    summary: dict[str, dict] = {}
    for provider_name, provider_payload in providers.items():
        normalized_name = _normalize_string(provider_name)
        if normalized_name is None or not isinstance(provider_payload, dict):
            continue
        api_key = _normalize_string(provider_payload.get("api_key"))
        admin_key = _normalize_string(provider_payload.get("admin_key"))
        user_identifier = _normalize_string(provider_payload.get("user_identifier"))
        summary[normalized_name] = {
            "configured": bool(api_key or admin_key or user_identifier),
            "has_api_key": api_key is not None,
            "has_admin_key": admin_key is not None,
            "api_key_hint": _mask_secret(api_key),
            "admin_key_hint": _mask_secret(admin_key),
            "user_identifier": user_identifier,
            "default_model_id": _normalize_string(provider_payload.get("default_model_id")),
            "selected_model_ids": _normalize_string_list(provider_payload.get("selected_model_ids")),
            "updated_at": _normalize_string(provider_payload.get("updated_at")),
        }
    return {"configured": bool(summary), "providers": summary}


class ProviderCredentialsStore:
    def __init__(self, *, path: str, logger) -> None:
        self._path = Path(path)
        self._logger = logger

    def load(self) -> Optional[dict]:
        if not self._path.exists():
            return None
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            if hasattr(self._logger, "warning"):
                self._logger.warning(
                    "[provider-credentials-invalid] %s",
                    {"path": str(self._path), "reason": "invalid_json"},
                )
            return None
        is_valid, error = validate_provider_credentials(payload)
        if not is_valid:
            if hasattr(self._logger, "warning"):
                self._logger.warning(
                    "[provider-credentials-invalid] %s",
                    {"path": str(self._path), "reason": error},
                )
            return None
        return payload

    def load_or_create(self) -> dict:
        existing = self.load()
        if existing is not None:
            return existing
        created = create_provider_credentials_payload()
        self.save(created)
        return created

    def save(self, payload: dict) -> None:
        is_valid, error = validate_provider_credentials(payload)
        if not is_valid:
            raise ValueError(f"cannot save invalid provider credentials payload: {error}")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._path.with_suffix(f"{self._path.suffix}.tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.chmod(tmp_path, 0o600)
        tmp_path.replace(self._path)
        try:
            os.chmod(self._path, 0o600)
        except OSError:
            pass
        if hasattr(self._logger, "info"):
            self._logger.info("[provider-credentials-saved] %s", {"path": str(self._path)})

    def upsert_openai_credentials(
        self,
        *,
        api_key: str,
        admin_key: str | None = None,
        user_identifier: str | None = None,
    ) -> dict:
        normalized_api_key = _normalize_string(api_key)
        if normalized_api_key is None:
            raise ValueError("api_key is required")
        payload = self.load_or_create()
        providers = payload.setdefault("providers", {})
        providers["openai"] = {
            "api_key": normalized_api_key,
            "admin_key": _normalize_string(admin_key),
            "user_identifier": _normalize_string(user_identifier),
            "default_model_id": _normalize_string((providers.get("openai") or {}).get("default_model_id")),
            "selected_model_ids": _normalize_string_list((providers.get("openai") or {}).get("selected_model_ids")),
            "updated_at": _iso_now(),
        }
        self.save(payload)
        return payload

    def update_openai_preferences(
        self,
        *,
        default_model_id: str | None = None,
        selected_model_ids: list[str] | None = None,
    ) -> dict:
        payload = self.load_or_create()
        providers = payload.setdefault("providers", {})
        existing = providers.get("openai")
        if not isinstance(existing, dict):
            existing = {
                "api_key": None,
                "admin_key": None,
                "user_identifier": None,
                "default_model_id": None,
                "selected_model_ids": [],
                "updated_at": _iso_now(),
            }
        normalized_selected = _normalize_string_list(selected_model_ids) if selected_model_ids is not None else _normalize_string_list(existing.get("selected_model_ids"))
        normalized_default = _normalize_string(default_model_id)
        if normalized_default and normalized_default not in normalized_selected:
            normalized_selected = [normalized_default, *normalized_selected]
        if not normalized_default:
            normalized_default = normalized_selected[0] if normalized_selected else None
        existing["default_model_id"] = normalized_default
        existing["selected_model_ids"] = normalized_selected
        existing["updated_at"] = _iso_now()
        providers["openai"] = existing
        self.save(payload)
        return payload
