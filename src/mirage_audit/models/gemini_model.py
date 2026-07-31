"""Google Gemini vision model adapter for Mirage Audit."""

import os
import time
from typing import Optional

from PIL import Image

from mirage_audit.models.base import BaseVLMModel


class GeminiVLMModel(BaseVLMModel):
    """Adapter for Google Gemini vision models (e.g. gemini-1.5-flash, gemini-1.5-pro)."""

    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        api_key: Optional[str] = None,
        max_retries: int = 3,
    ):
        super().__init__(model_name)
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError(
                "Gemini support requires 'google-generativeai'. Install with: "
                "pip install mirage-audit[gemini]"
            ) from exc

        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY.")

        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model_name)
        self.max_retries = max_retries

    def generate(self, image: Optional[Image.Image], prompt: str) -> str:
        generation_config = {
            "max_output_tokens": 512,
            "temperature": 0.0,
        }

        for attempt in range(self.max_retries):
            try:
                if image is None:
                    response = self.client.generate_content(
                        prompt, generation_config=generation_config
                    )
                else:
                    response = self.client.generate_content(
                        [prompt, image], generation_config=generation_config
                    )
                response.resolve()
                return response.text.strip()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"Gemini API call failed after {self.max_retries} attempts: {e}"
                    ) from e
                time.sleep(2**attempt)

        return ""
