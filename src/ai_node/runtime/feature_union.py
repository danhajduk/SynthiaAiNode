from ai_node.providers.model_feature_schema import create_default_feature_flags


def build_feature_union(*, model_feature_entries: list[dict], enabled_models: list[str] | None = None) -> dict[str, bool]:
    feature_union = create_default_feature_flags()
    enabled_set = {
        str(model_id or "").strip().lower()
        for model_id in (enabled_models or [])
        if str(model_id or "").strip()
    }
    for entry in model_feature_entries:
        if not isinstance(entry, dict):
            continue
        model_id = str(entry.get("model_id") or "").strip().lower()
        if enabled_set and model_id not in enabled_set:
            continue
        features = entry.get("features")
        if not isinstance(features, dict):
            continue
        for feature_name, value in features.items():
            key = str(feature_name or "").strip()
            if key in feature_union and bool(value):
                feature_union[key] = True
    return feature_union
