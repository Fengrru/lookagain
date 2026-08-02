"""Factory for instantiating judge adapters by provider name."""

from typing import Optional

from lookagain.judge.anthropic_judge import AnthropicJudge
from lookagain.judge.base import BaseJudge
from lookagain.judge.gemini_judge import GeminiJudge
from lookagain.judge.openai_judge import OpenAIJudge

PROVIDERS = {
    "openai": OpenAIJudge,
    "anthropic": AnthropicJudge,
    "gemini": GeminiJudge,
    "http": OpenAIJudge,  # OpenAI-compatible endpoint
}


def create_judge(
    provider: str,
    model_name: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> BaseJudge:
    """Create a judge adapter for the given provider.

    Each provider uses a native adapter that talks to the correct API:
      - openai   -> OpenAIJudge (OpenAI Chat Completions API)
      - anthropic -> AnthropicJudge (Anthropic Messages API)
      - gemini   -> GeminiJudge (Google Generative AI API)
      - http     -> OpenAIJudge (OpenAI-compatible local server)

    Args:
        provider: One of "openai", "anthropic", "gemini", "http".
        model_name: Judge model identifier.
        api_key: Optional API key.
        base_url: Optional base URL (used for HTTP provider).

    Returns:
        An instance of BaseJudge.
    """
    provider = provider.lower()
    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown judge provider '{provider}'. Supported: {', '.join(PROVIDERS.keys())}"
        )

    kwargs = {"model_name": model_name}
    if api_key is not None:
        kwargs["api_key"] = api_key

    # HTTP judge targets a local OpenAI-compatible server.
    if provider == "http" and base_url is not None:
        from openai import OpenAI

        judge = OpenAIJudge(**kwargs)
        judge.client = OpenAI(api_key=api_key or "not-needed", base_url=base_url)
        return judge

    return PROVIDERS[provider](**kwargs)


def list_providers() -> list[str]:
    """Return supported judge provider names."""
    return list(PROVIDERS.keys())
