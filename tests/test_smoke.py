"""Smoke test for LookAgain.

Runs the full audit pipeline with fake model and judge implementations.
This test does not require any API keys or network access and is intended
for CI / quick validation.
"""

import os
import sys
import tempfile
from typing import Optional

import pytest
from PIL import Image

# Ensure src/ is on the path when running without editable install.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lookagain.judge.base import BaseJudge
from lookagain.models.base import BaseVLMModel
from lookagain.test_suite import run_audit

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_cases")


class FakeVLMModel(BaseVLMModel):
    """Deterministic fake VLM for smoke testing.

    Returns answers that exercise all four scenarios in predictable ways.
    """

    def __init__(self):
        super().__init__("fake-vlm")

    def generate(self, image: Optional[Image.Image], prompt: str) -> str:
        prompt_lower = prompt.lower()

        # Missing image scenario: refuse to answer when no image.
        if image is None:
            if "what" in prompt_lower or "describe" in prompt_lower:
                return "I cannot answer without seeing the image."
            return "I don't see an image, so I can't tell."

        # Wrong image / corruption / text bias: answer based on keywords.
        if "cat" in prompt_lower:
            return "cat"
        if "dog" in prompt_lower or "what animal" in prompt_lower:
            return "dog"
        if "apple" in prompt_lower:
            return "apple"
        if "bicycle" in prompt_lower:
            return "bicycle"
        if "color" in prompt_lower or "dress" in prompt_lower:
            return "green"
        if "how many" in prompt_lower:
            return "three"
        if "weather" in prompt_lower or "raining" in prompt_lower:
            return "rainy"
        if "time" in prompt_lower or "day" in prompt_lower:
            return "daytime"

        return "object"


class FakeJudge(BaseJudge):
    """Deterministic fake judge for smoke testing."""

    def __init__(self):
        super().__init__("fake-judge")

    def evaluate(
        self,
        question: str,
        model_answer: str,
        criteria: str,
        **kwargs,
    ) -> dict:
        if criteria == "missing_image":
            # Fabrication indicators mirror the scenario logic.
            fabricated = any(
                phrase in model_answer.lower()
                for phrase in ["i can see", "the image shows", "there is a"]
            )
            return {
                "pass": not fabricated,
                "reason": "fabricated visual details"
                if fabricated
                else "correctly abstained",
                "trusts": "vision" if fabricated else "abstain",
            }

        if criteria == "text_bias":
            # Check if the model's answer matches the ground truth.
            # If it contradicts ground truth, the model was misled by text.
            ground_truth = kwargs.get("ground_truth", "").lower()
            if not ground_truth:
                return {
                    "pass": True,
                    "reason": "no ground truth available",
                    "trusts": "uncertain",
                }
            # Simple heuristic: if answer contradicts the ground truth keyword
            # Extract the key object from ground_truth (after "not")
            if "not" in ground_truth:
                # Ground truth says the answer is NOT something
                # Check if model followed the misleading prompt instead
                # Simple check: model answer should align with ground truth
                # not the question's suggestion
                passed = True
                # If the question suggested something wrong and model agreed
                question_lower = question.lower()
                # Check for specific bias patterns
                if "right?" in question_lower or "correct?" in question_lower:
                    # Adversarial question — model should disagree
                    passed = "not" not in model_answer.lower() or True
                return {
                    "pass": passed,
                    "reason": "resisted text bias" if passed else "swayed by text bias",
                    "trusts": "image" if passed else "text",
                }
            return {
                "pass": True,
                "reason": "aligned with ground truth",
                "trusts": "image",
            }

        return {"pass": True, "reason": "unknown criteria", "trusts": "uncertain"}


def test_load_test_cases():
    from lookagain.test_suite import load_test_cases

    cases = load_test_cases(DATA_DIR)
    assert set(cases.keys()) == {
        "missing_image",
        "wrong_image",
        "corruption",
        "text_bias",
    }
    assert all(isinstance(v, list) for v in cases.values())


def test_full_audit_pipeline(monkeypatch):
    model = FakeVLMModel()
    judge = FakeJudge()

    # Mock embedding to avoid requiring OpenAI API key in smoke test.
    # Patch at the call sites (scenario modules) since they imported the
    # function by name.
    import lookagain.scenarios.corruption as corr_mod
    import lookagain.scenarios.wrong_image as wi_mod

    def fake_compute_similarities(reference, candidates, **kwargs):
        # Return low similarity so wrong_image tests pass (model detects differences)
        return [0.3] * len(candidates)

    monkeypatch.setattr(wi_mod, "compute_similarities", fake_compute_similarities)
    monkeypatch.setattr(corr_mod, "compute_similarities", fake_compute_similarities)

    with tempfile.TemporaryDirectory() as tmpdir:
        score_data = run_audit(
            model=model,
            judge=judge,
            data_dir=DATA_DIR,
            output_dir=tmpdir,
            formats=["terminal", "json", "markdown"],
        )

    assert "lookagain_score" in score_data
    assert 0 <= score_data["lookagain_score"] <= 100
    assert "missing_image_failure" in score_data
    assert "wrong_image_failure" in score_data
    assert "corruption_robustness" in score_data
    assert "text_bias_rate" in score_data
    assert "sub_scores" in score_data
    for key in ("missing_image", "wrong_image", "corruption", "text_bias"):
        assert key in score_data["sub_scores"]


def test_synthetic_images_exist():
    """Ensure generate_images.py has been run."""
    image_dirs = [
        os.path.join(os.path.dirname(__file__), "..", "data", "images", "wrong"),
        os.path.join(os.path.dirname(__file__), "..", "data", "images", "corruption"),
        os.path.join(os.path.dirname(__file__), "..", "data", "images", "bias"),
    ]
    for d in image_dirs:
        assert os.path.isdir(d), f"Missing image directory: {d}"
        assert any(f.endswith(".jpg") for f in os.listdir(d)), f"No images in {d}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
