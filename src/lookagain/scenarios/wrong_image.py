"""Wrong Image test scenario.

Tests whether the model's answer changes when given a wrong image.
Uses embedding similarity: high similarity between correct-image and
wrong-image answers → model ignored the visual input (FAIL).
"""

from ..utils.embedding import compute_similarities
from ..utils.image_utils import load_image
from .base import BaseScenario, TestResult

# Threshold: if the MAXIMUM similarity between correct-image and wrong-image
# answers is above this threshold, the model is likely NOT relying on visual input.
# We check max_sim because if ANY wrong image causes a sufficiently different answer,
# it means the model CAN detect visual differences.
SIMILARITY_THRESHOLD = 0.70


class WrongImageScenario(BaseScenario):
    """Wrong Image test: compare answers across correct and wrong images."""

    def __init__(self):
        super().__init__("wrong_image")

    def run(self, model, judge, test_cases: list[dict]) -> list[TestResult]:
        self.results = []

        for tc in test_cases:
            question = tc["question"]
            test_id = tc["id"]
            risk_category = tc.get("risk_category", "")

            correct_image_path = tc.get("correct_image_path", "")
            wrong_image_paths = tc.get("wrong_image_paths", [])

            # Load images
            correct_img = load_image(correct_image_path)
            wrong_imgs = [load_image(p) for p in wrong_image_paths]
            wrong_imgs = [img for img in wrong_imgs if img is not None]

            if correct_img is None or not wrong_imgs:
                self.results.append(
                    TestResult(
                        test_id=test_id,
                        scenario="wrong_image",
                        passed=False,
                        reason="Missing image files",
                        risk_category=risk_category,
                    )
                )
                continue

            # Get answers
            answer_correct = model.generate(image=correct_img, prompt=question)
            answers_wrong = [
                model.generate(image=img, prompt=question) for img in wrong_imgs
            ]

            # Compute similarity between correct answer and each wrong answer
            similarities = compute_similarities(answer_correct, answers_wrong)
            max_sim = max(similarities) if similarities else 1.0
            avg_sim = sum(similarities) / len(similarities) if similarities else 1.0

            # If the MAXIMUM similarity is below threshold, it means at least one
            # wrong image caused a different answer, so the model IS detecting
            # visual differences. PASS.
            passed = max_sim < SIMILARITY_THRESHOLD

            reason = (
                f"Correct vs wrong-image answer similarity: max={max_sim:.2f}, "
                f"avg={avg_sim:.2f}. "
                + (
                    "Model detected visual differences."
                    if passed
                    else "Model may be ignoring visual input."
                )
            )

            self.results.append(
                TestResult(
                    test_id=test_id,
                    scenario="wrong_image",
                    passed=passed,
                    reason=reason,
                    risk_category=risk_category,
                    details={
                        "question": question,
                        "answer_correct": answer_correct,
                        "answers_wrong": answers_wrong,
                        "similarities": similarities,
                        "max_similarity": max_sim,
                        "avg_similarity": avg_sim,
                    },
                )
            )

        return self.results
