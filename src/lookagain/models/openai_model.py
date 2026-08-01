"""OpenAI VLM adapter (GPT-4o, GPT-4V)."""

import base64
import io
import time
from typing import Optional

from openai import OpenAI
from PIL import Image

from .base import BaseVLMModel


class OpenAIVLMModel(BaseVLMModel):
    """OpenAI GPT-4o / GPT-4V model adapter.

    Args:
        model_name: OpenAI model ID, e.g. "gpt-4o", "gpt-4-turbo".
        api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        max_retries: Max retries on rate-limit or transient errors.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        max_retries: int = 3,
    ):
        super().__init__(model_name)
        self.client = OpenAI(api_key=api_key)
        self.max_retries = max_retries

    def generate(self, image: Optional[Image.Image], prompt: str) -> str:
        """Call OpenAI Chat Completions API with optional image.

        If image is None, sends a text-only message (Missing Image scenario).
        """
        content = self._build_content(image, prompt)

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": content}],
                    max_tokens=512,
                    temperature=0.0,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"OpenAI API call failed after {self.max_retries} attempts: {e}"
                    ) from e
                time.sleep(2**attempt)

        return ""  # unreachable

    def _build_content(self, image: Optional[Image.Image], prompt: str) -> list:
        """Build the content list for the OpenAI API."""
        if image is None:
            return [{"type": "text", "text": prompt}]

        # Encode image to base64 data URL
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        data_url = f"data:image/png;base64,{img_base64}"

        return [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": data_url, "detail": "auto"},
            },
        ]
