"""Text Bias test scenario.

Tests whether misleading text prompts cause the model to ignore image content.
Uses LLM-as-Judge exclusively (rules cannot handle semantic conflict detection).
"""

from typing import Dict, List

from ..utils.image_utils import load_image
from .base import BaseScenario, TestResult


class TextBiasScenario(BaseScenario):
    """Text Bias test: misleading prompts vs. image content."""

    def __init__(self):
        super().__init__("text_bias")

    def run(self, model, judge, test_cases: List[Dict]) -> List[TestResult]:
        """Run text bias tests. Requires judge — cannot use rules alone."""
        self.results = []

        for tc in test_cases:
            question = tc["question"]
            test_id = tc["id"]
            risk_category = tc.get("risk_category", "")
            image_path = tc.get("image_path", "")
            ground_truth = tc.get("ground_truth", "")

            img = load_image(image_path)
            if img is None:
                self.results.append(
                    TestResult(
                        test_id=test_id,
                        scenario="text_bias",
                        passed=False,
                        reason="Missing image file",
                        risk_category=risk_category,
                    )
                )
                continue

            # Generate answer with misleading prompt + correct image
            answer = model.generate(image=img, prompt=question)

            if judge is None:
                # Cannot evaluate text bias without judge
                self.results.append(
                    TestResult(
                        test_id=test_id,
                        scenario="text_bias",
                        passed=False,
                        reason="No judge available for text bias evaluation",
                        risk_category=risk_category,
                        details={"question": question, "answer": answer},
                    )
                )
                continue

            # Judge evaluation
            eval_result = judge.evaluate(
                question=question,
                model_answer=answer,
                criteria="text_bias",
                ground_truth=ground_truth,
            )

            self.results.append(
                TestResult(
                    test_id=test_id,
                    scenario="text_bias",
                    passed=eval_result["pass"],
                    reason=eval_result["reason"],
                    risk_category=risk_category,
                    trusts=eval_result.get("trusts", "uncertain"),
                    details={
                        "question": question,
                        "answer": answer,
                        "ground_truth": ground_truth,
                    },
                )
            )

        return self.results
