"""Anthropic Claude Judge implementation."""

import json
import os
import time
from typing import Optional

from .base import BaseJudge
from .prompts import MISSING_IMAGE_JUDGE_PROMPT, TEXT_BIAS_JUDGE_PROMPT


class AnthropicJudge(BaseJudge):
    """Anthropic Claude Judge for evaluating model answer reliability.

    Args:
        model_name: Anthropic model ID for the judge, e.g. "claude-3-5-sonnet-20241022".
        api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        max_retries: Max retries on API errors.
    """

    PROMPT_MAP = {
        "missing_image": MISSING_IMAGE_JUDGE_PROMPT,
        "text_bias": TEXT_BIAS_JUDGE_PROMPT,
    }

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
                "pip install lookagain[anthropic]"
            ) from exc

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.max_retries = max_retries

    def evaluate(
        self,
        question: str,
        model_answer: str,
        criteria: str,
        **kwargs,
    ) -> dict:
        """Evaluate model answer against criteria using Claude.

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

        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=256,
                    temperature=0.0,
                    messages=[{"role": "user", "content": prompt_text}],
                )
                texts = [
                    block.text for block in response.content if block.type == "text"
                ]
                content = "\n".join(texts).strip()
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
