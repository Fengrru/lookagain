"""GPT-4o Judge implementation."""

import json
import time
from typing import Dict, Optional

from openai import OpenAI

from .base import BaseJudge
from .prompts import MISSING_IMAGE_JUDGE_PROMPT, TEXT_BIAS_JUDGE_PROMPT


class OpenAIJudge(BaseJudge):
    """GPT-4o Judge for evaluating model answer reliability.

    Args:
        model_name: OpenAI model ID for the judge, e.g. "gpt-4o".
        api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        max_retries: Max retries on API errors.
    """

    PROMPT_MAP = {
        "missing_image": MISSING_IMAGE_JUDGE_PROMPT,
        "text_bias": TEXT_BIAS_JUDGE_PROMPT,
    }

    def __init__(
        self,
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        max_retries: int = 3,
    ):
        super().__init__(model_name)
        self.client = OpenAI(api_key=api_key)
        self.max_retries = max_retries

    def evaluate(
        self,
        question: str,
        model_answer: str,
        criteria: str,
        **kwargs,
    ) -> Dict:
        """Evaluate model answer against criteria using GPT-4o.

        Args:
            question: The original question.
            model_answer: The model's text response.
            criteria: One of "missing_image" or "text_bias".
            **kwargs: Additional template variables (ground_truth, etc.)

        Returns:
            dict with keys: "pass" (bool), "reason" (str)
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
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt_text}],
                    max_tokens=256,
                    temperature=0.0,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content or "{}"
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
