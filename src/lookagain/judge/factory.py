"""Factory for instantiating judge adapters by provider name."""

from lookagain.judge.base import BaseJudge
from lookagain.judge.openai_judge import OpenAIJudge

PROVIDERS = {
    "openai": OpenAIJudge,
    "anthropic": OpenAIJudge,  # Reuse OpenAIJudge shape via underlying client
    "gemini": OpenAIJudge,
    "http": OpenAIJudge,
}


def create_judge(
    provider: str,
    model_name: str,
    api_key: str | None = None,
    base_url: str | None = None,
) -> BaseJudge:
    """Create a judge adapter.

    For now all providers are backed by OpenAIJudge because the judge only
    needs text-in/text-out. For Anthropic/Gemini/HTTP the caller can provide
    the corresponding api_key/base_url and model_name.

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

    # HTTP judge can target a local OpenAI-compatible server.
    if provider == "http" and base_url is not None:
        from openai import OpenAI

        judge = OpenAIJudge(**kwargs)
        judge.client = OpenAI(api_key=api_key or "not-needed", base_url=base_url)
        return judge

    return PROVIDERS[provider](**kwargs)


def list_providers() -> list[str]:
    """Return supported judge provider names."""
    return list(PROVIDERS.keys())
