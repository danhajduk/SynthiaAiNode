OPENAI_PRICING_CATALOG = {
    "gpt-5.2": {"input_per_1m_tokens": 1.75, "output_per_1m_tokens": 14.0, "currency": "usd"},
    "gpt-5.1": {"input_per_1m_tokens": 1.25, "output_per_1m_tokens": 10.0, "currency": "usd"},
    "gpt-5": {"input_per_1m_tokens": 1.25, "output_per_1m_tokens": 10.0, "currency": "usd"},
    "gpt-5-mini": {"input_per_1m_tokens": 0.25, "output_per_1m_tokens": 2.0, "currency": "usd"},
    "gpt-5-nano": {"input_per_1m_tokens": 0.05, "output_per_1m_tokens": 0.4, "currency": "usd"},
    "gpt-5.2-chat-latest": {"input_per_1m_tokens": 1.75, "output_per_1m_tokens": 14.0, "currency": "usd"},
    "gpt-5.1-chat-latest": {"input_per_1m_tokens": 1.25, "output_per_1m_tokens": 10.0, "currency": "usd"},
    "gpt-5-chat-latest": {"input_per_1m_tokens": 1.25, "output_per_1m_tokens": 10.0, "currency": "usd"},
    "gpt-5.2-codex": {"input_per_1m_tokens": 1.75, "output_per_1m_tokens": 14.0, "currency": "usd"},
    "gpt-5.1-codex-max": {"input_per_1m_tokens": 1.25, "output_per_1m_tokens": 10.0, "currency": "usd"},
    "gpt-5.1-codex": {"input_per_1m_tokens": 1.25, "output_per_1m_tokens": 10.0, "currency": "usd"},
    "gpt-5-codex": {"input_per_1m_tokens": 1.25, "output_per_1m_tokens": 10.0, "currency": "usd"},
    "gpt-5.2-pro": {"input_per_1m_tokens": 21.0, "output_per_1m_tokens": 168.0, "currency": "usd"},
    "gpt-5-pro": {"input_per_1m_tokens": 15.0, "output_per_1m_tokens": 120.0, "currency": "usd"},
    "gpt-4.1": {"input_per_1m_tokens": 2.0, "output_per_1m_tokens": 8.0, "currency": "usd"},
    "gpt-4.1-mini": {"input_per_1m_tokens": 0.4, "output_per_1m_tokens": 1.6, "currency": "usd"},
    "gpt-4.1-nano": {"input_per_1m_tokens": 0.1, "output_per_1m_tokens": 0.4, "currency": "usd"},
    "gpt-4o": {"input_per_1m_tokens": 2.5, "output_per_1m_tokens": 10.0, "currency": "usd"},
    "gpt-4o-mini": {"input_per_1m_tokens": 0.15, "output_per_1m_tokens": 0.6, "currency": "usd"},
    "gpt-realtime": {"input_per_1m_tokens": 4.0, "output_per_1m_tokens": 16.0, "currency": "usd"},
    "gpt-realtime-mini": {"input_per_1m_tokens": 0.6, "output_per_1m_tokens": 2.4, "currency": "usd"},
}


def get_openai_model_pricing(model_id: str) -> dict | None:
    normalized = str(model_id or "").strip()
    if not normalized:
        return None
    pricing = OPENAI_PRICING_CATALOG.get(normalized)
    if pricing is None:
        return None
    return dict(pricing)
