"""Anthropic Claude vision model adapter for Mirage Audit."""

import base64
import io
import os
import time
from typing import Optional

from PIL import Image

from mirage_audit.models.base import BaseVLMModel


class AnthropicVLMModel(BaseVLMModel):
    """Adapter for Anthropic Claude vision models (e.g. claude-3-opus, claude-3-5-sonnet)."""

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        max_retries: int = 3,
    ):
        super().__init__(model_name)
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "Anthropic support requires 'anthropic'. Install with: "
                "pip install mirage-audit[anthropic]"
            ) from exc

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.max_retries = max_retries

    def _encode_image(self, image: Image.Image) -> tuple[str, str]:
        """Return (media_type, base64_data) for a PIL image."""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return "image/png", data

    def generate(self, image: Optional[Image.Image], prompt: str) -> str:
        content: list[dict]
        if image is None:
            content = [{"type": "text", "text": prompt}]
        else:
            media_type, data = self._encode_image(image)
            content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": data,
                    },
                },
                {"type": "text", "text": prompt},
            ]

        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=512,
                    temperature=0.0,
                    messages=[{"role": "user", "content": content}],
                )
                texts = [
                    block.text for block in response.content if block.type == "text"
                ]
                return "\n".join(texts).strip()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"Anthropic API call failed after {self.max_retries} attempts: {e}"
                    ) from e
                time.sleep(2**attempt)

        return ""
