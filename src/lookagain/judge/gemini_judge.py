"""Google Gemini Judge implementation."""

import json
import os
import time
from typing import Optional

from .base import BaseJudge
from .prompts import MISSING_IMAGE_JUDGE_PROMPT, TEXT_BIAS_JUDGE_PROMPT


class GeminiJudge(BaseJudge):
    """Google Gemini Judge for evaluating model answer reliability.

    Args:
        model_name: Gemini model ID for the judge, e.g. "gemini-1.5-flash".
        api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
        max_retries: Max retries on API errors.
    """

    PROMPT_MAP = {
        "missing_image": MISSING_IMAGE_JUDGE_PROMPT,
        "text_bias": TEXT_BIAS_JUDGE_PROMPT,
    }

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
                "pip install lookagain[gemini]"
            ) from exc

        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY.")

        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model_name)
        self.max_retries = max_retries

    def evaluate(
        self,
        question: str,
        model_answer: str,
        criteria: str,
        **kwargs,
    ) -> dict:
        """Evaluate model answer against criteria using Gemini.

        Args:
            question: The original question.
            model_answer: The model's text response.
            criteria: One of "missing_image" or "text_bias".
            **kwargs: Additional template variables (ground_truth, etc.)

        Returns:
            dict with keys: "pass" (bool), "reason" (str), "trusts" (str)
        """
        if criteria not in self.PROMPT_MAP:
            raise ValueError(
                f"Unknown criteria: {criteria}. Choose from {list(self.PROMPT_MAP)}"
            )

        template = self.PROMPT_MAP[criteria]
        prompt_text = template.format(
            question=question,
            model_answer=model_answer,
            **kwargs,
        )

        generation_config = {
            "max_output_tokens": 256,
            "temperature": 0.0,
        }

        for attempt in range(self.max_retries):
            try:
                response = self.client.generate_content(
                    prompt_text,
                    generation_config=generation_config,
                )
                response.resolve()
                content = response.text.strip()
                result = json.loads(content)
                return {
                    "pass": result.get("pass", False),
                    "reason": result.get("reason", "No reason provided"),
                    "trusts": result.get("trusts", "uncertain"),
                }
            except (json.JSONDecodeError, Exception) as e:
                if attempt == self.max_retries - 1:
                    return {
                        "pass": False,
                        "reason": f"Judge evaluation failed: {e}",
                        "trusts": "uncertain",
                    }
                time.sleep(2**attempt)

        return {"pass": False, "reason": "Judge failed", "trusts": "uncertain"}
