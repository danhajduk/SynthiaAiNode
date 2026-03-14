import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from ai_node.providers.model_feature_schema import create_default_feature_flags, normalize_feature_flags


DEFAULT_PROVIDER_MODEL_FEATURES_PATH = "providers/openai/provider_model_features.json"
PROVIDER_MODEL_FEATURES_SCHEMA_VERSION = "1.0"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProviderModelFeatureEntry(BaseModel):
    model_id: str
    provider: str = "openai"
    features: dict[str, bool] = Field(default_factory=create_default_feature_flags)
    classification_model: str | None = None
    classified_at: str = Field(default_factory=_iso_now)


class ProviderModelFeatureCatalog(BaseModel):
    schema_version: str = PROVIDER_MODEL_FEATURES_SCHEMA_VERSION
    generated_at: str = Field(default_factory=_iso_now)
    entries: list[ProviderModelFeatureEntry] = Field(default_factory=list)


class ProviderModelFeatureCatalogStore:
    def __init__(self, *, path: str = DEFAULT_PROVIDER_MODEL_FEATURES_PATH, logger) -> None:
        self._path = Path(path)
        self._logger = logger

    def load(self) -> ProviderModelFeatureCatalog | None:
        if not self._path.exists():
            return None
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            return ProviderModelFeatureCatalog.model_validate(payload)
        except Exception:
            return None

    def payload(self) -> dict:
        snapshot = self.load()
        if snapshot is None:
            return {
                "schema_version": PROVIDER_MODEL_FEATURES_SCHEMA_VERSION,
                "generated_at": _iso_now(),
                "entries": [],
                "source": "provider_model_features",
            }
        return {
            "schema_version": snapshot.schema_version,
            "generated_at": snapshot.generated_at,
            "entries": [entry.model_dump() for entry in snapshot.entries],
            "source": "provider_model_features",
        }

    def save_entries(
        self,
        *,
        provider: str,
        classification_model: str | None,
        entries: list[dict],
        classified_at: str | None = None,
    ) -> ProviderModelFeatureCatalog:
        provider_id = str(provider or "openai").strip().lower() or "openai"
        timestamp = str(classified_at or _iso_now()).strip() or _iso_now()
        normalized_entries: list[ProviderModelFeatureEntry] = []
        seen: set[str] = set()
        for item in entries:
            if not isinstance(item, dict):
                continue
            model_id = str(item.get("model_id") or "").strip().lower()
            if not model_id or model_id in seen:
                continue
            feature_flags = item.get("features")
            if isinstance(feature_flags, dict):
                normalized_flags = normalize_feature_flags(feature_flags=feature_flags)
            else:
                normalized_flags = create_default_feature_flags()
            normalized_entries.append(
                ProviderModelFeatureEntry(
                    model_id=model_id,
                    provider=provider_id,
                    features=normalized_flags,
                    classification_model=str(classification_model or "").strip() or None,
                    classified_at=timestamp,
                )
            )
            seen.add(model_id)
        normalized_entries.sort(key=lambda entry: entry.model_id)
        snapshot = ProviderModelFeatureCatalog(generated_at=timestamp, entries=normalized_entries)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(snapshot.model_dump(), indent=2, sort_keys=True), encoding="utf-8")
        if hasattr(self._logger, "info"):
            self._logger.info(
                "[provider-model-feature-catalog-saved] %s",
                {"path": str(self._path), "entries": len(snapshot.entries)},
            )
        return snapshot
