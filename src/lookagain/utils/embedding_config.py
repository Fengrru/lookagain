"""Global embedding configuration for LookAgain.

Allows scenarios to use the configured embedding model and API key
without threading config objects through every call.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EmbeddingSettings:
    """Runtime embedding settings."""

    api_key: Optional[str] = None
    model: str = "text-embedding-3-small"
    base_url: Optional[str] = None


# Global singleton — set once by the CLI at startup
_settings = EmbeddingSettings()


def configure_embedding(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> None:
    """Set the global embedding configuration.

    Called by the CLI during audit setup to share embedding settings
    with all scenario callers.

    Args:
        api_key: OpenAI API key for embeddings.
        model: Embedding model name.
        base_url: Optional base URL for custom endpoints.
    """
    global _settings
    if api_key is not None:
        _settings.api_key = api_key
    if model is not None:
        _settings.model = model
    if base_url is not None:
        _settings.base_url = base_url


def get_embedding_settings() -> EmbeddingSettings:
    """Get the current global embedding settings."""
    return _settings
