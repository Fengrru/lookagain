"""VLM model abstraction layer."""

from .base import BaseVLMModel
from .openai_model import OpenAIVLMModel

__all__ = ["BaseVLMModel", "OpenAIVLMModel"]
