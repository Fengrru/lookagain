"""Generic HTTP/OpenAI-compatible vision model adapter for LookAgain.

Supports local servers such as vLLM, LMDeploy, Ollama (with OpenAI endpoint),
or any provider exposing the `/v1/chat/completions` endpoint.
"""

import base64
import io
import os
import time
from typing import Optional

from PIL import Image

from lookagain.models.base import BaseVLMModel


class HTTPVLMModel(BaseVLMModel):
    """Adapter for OpenAI-compatible HTTP endpoints."""

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
    ):
        super().__init__(model_name)
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "HTTP adapter is implemented via the OpenAI client. Install with: "
                "pip install lookagain[openai]"
            ) from exc

        self.base_url = base_url or os.environ.get("MIRAGE_HTTP_BASE_URL")
        if not self.base_url:
            raise ValueError(
                "base_url is required. Set MIRAGE_HTTP_BASE_URL or pass --base-url."
            )

        key = api_key or os.environ.get("MIRAGE_HTTP_API_KEY", "not-needed")
        self.client = OpenAI(api_key=key, base_url=self.base_url)
        self.max_retries = max_retries

    def _encode_image(self, image: Image.Image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{data}"

    def generate(self, image: Optional[Image.Image], prompt: str) -> str:
        content = [{"type": "text", "text": prompt}]
        if image is not None:
            content.insert(
                0,
                {"type": "image_url", "image_url": {"url": self._encode_image(image)}},
            )

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": content}],
                    max_tokens=512,
                    temperature=0.0,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"HTTP API call failed after {self.max_retries} attempts: {e}"
                    ) from e
                time.sleep(2**attempt)

        return ""
