"""Abstract base class for LLM-as-Judge evaluators."""

from abc import ABC, abstractmethod


class BaseJudge(ABC):
    """Abstract Judge interface.

    The Judge evaluates whether the model's answer meets specific
    reliability criteria (e.g., "did the model fabricate visual details?").
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def evaluate(
        self,
        question: str,
        model_answer: str,
        criteria: str,
        **kwargs,
    ) -> dict:
        """Evaluate the model's answer against given criteria.

        Args:
            question: The original question asked to the model.
            model_answer: The model's text response.
            criteria: What to check for (e.g. "fabricated_visual_details").
            **kwargs: Additional context (image_description, ground_truth, etc.)

        Returns:
            dict with keys: "pass" (bool), "reason" (str)
        """
        ...
