"""Factory for instantiating VLM adapters by provider name."""

from lookagain.models.anthropic_model import AnthropicVLMModel
from lookagain.models.base import BaseVLMModel
from lookagain.models.gemini_model import GeminiVLMModel
from lookagain.models.http_model import HTTPVLMModel
from lookagain.models.openai_model import OpenAIVLMModel


PROVIDERS = {
    "openai": OpenAIVLMModel,
    "anthropic": AnthropicVLMModel,
    "gemini": GeminiVLMModel,
    "http": HTTPVLMModel,
}


def create_model(provider: str, **kwargs) -> BaseVLMModel:
    """Create a VLM adapter for the given provider.

    Args:
        provider: One of "openai", "anthropic", "gemini", "http".
        **kwargs: Passed to the adapter constructor.

    Returns:
        An instance of BaseVLMModel.
    """
    provider = provider.lower()
    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. Supported: {', '.join(PROVIDERS.keys())}"
        )
    return PROVIDERS[provider](**kwargs)


def list_providers() -> list[str]:
    """Return supported provider names."""
    return list(PROVIDERS.keys())
