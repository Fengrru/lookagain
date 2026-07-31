"""Abstract base class for VLM model adapters."""

from abc import ABC, abstractmethod
from typing import Optional
from PIL import Image


class BaseVLMModel(ABC):
    """Abstract VLM interface for black-box auditing.

    All model adapters must implement generate().
    The audit tool does NOT access logits, gradients, or internal features.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate(self, image: Optional[Image.Image], prompt: str) -> str:
        """Generate a text response given an optional image and a prompt.

        Args:
            image: PIL Image, or None for text-only mode (Missing Image test).
            prompt: The text prompt / question.

        Returns:
            The model's text response as a string.
        """
        ...
