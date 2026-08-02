"""Image Corruption test scenario.

Tests answer stability under image degradations (blur, occlusion, low-res).
Measures embedding similarity decay between original-answer and each
corrupted-answer. Score = area under the similarity curve (higher = more robust).
"""

from ..utils.embedding import compute_similarities
from ..utils.embedding_config import get_embedding_settings
from ..utils.image_utils import generate_corruptions, load_image
from .base import BaseScenario, TestResult


class CorruptionScenario(BaseScenario):
    """Image Corruption test: measure answer stability under degradation."""

    CORRUPTION_NAMES = [
        "blur_light",
        "blur_medium",
        "blur_heavy",
        "occlusion",
        "center_occlusion",
        "low_res_50",
        "low_res_25",
    ]

    def __init__(self):
        super().__init__("corruption")

    def run(self, model, judge, test_cases: list[dict]) -> list[TestResult]:
        self.results = []

        for tc in test_cases:
            question = tc["question"]
            test_id = tc["id"]
            risk_category = tc.get("risk_category", "")
            image_path = tc.get("image_path", "")

            original_img = load_image(image_path)
            if original_img is None:
                self.results.append(
                    TestResult(
                        test_id=test_id,
                        scenario="corruption",
                        passed=False,
                        reason="Missing image file",
                        risk_category=risk_category,
                    )
                )
                continue

            # Generate corrupted versions
            corruptions = generate_corruptions(original_img)

            # Get original answer
            answer_original = model.generate(image=original_img, prompt=question)

            # Get answers for each corruption
            corruption_answers = {}
            for name, corrupted_img in corruptions.items():
                corruption_answers[name] = model.generate(
                    image=corrupted_img, prompt=question
                )

            # Compute similarities between original and each corruption
            names = list(corruption_answers.keys())
            emb = get_embedding_settings()
            sims = compute_similarities(
                answer_original,
                [corruption_answers[n] for n in names],
                api_key=emb.api_key,
                model=emb.model,
                base_url=emb.base_url,
            )

            # Curve area under similarity (simple mean)
            auc = sum(sims) / len(sims) if sims else 0.0

            # Score: AUC mapped to robustness. > 0.85 = PASS (high robustness)
            passed = auc >= 0.85

            # Find the corruption that caused the largest drop
            min_sim = min(sims) if sims else 1.0
            min_name = names[sims.index(min_sim)] if sims else ""

            reason = f"AUC={auc:.3f}, worst={min_name}({min_sim:.3f}). " + (
                "Model is robust to corruption."
                if passed
                else "Model degrades significantly under corruption."
            )

            self.results.append(
                TestResult(
                    test_id=test_id,
                    scenario="corruption",
                    passed=passed,
                    reason=reason,
                    risk_category=risk_category,
                    details={
                        "question": question,
                        "answer_original": answer_original,
                        "corruption_answers": corruption_answers,
                        "similarities": dict(zip(names, sims)),
                        "auc": auc,
                        "worst_corruption": min_name,
                        "worst_similarity": min_sim,
                    },
                )
            )

        return self.results

    @property
    def corruption_score(self) -> float:
        """Aggregate corruption robustness score (0–100).

        Calculated as the mean AUC across all test cases, scaled to 0–100.
        Returns 0.0 if no test cases have been run yet (no data = no
        robustness evidence, not a perfect score).
        """
        if not self.results:
            return 0.0
        auc_values = [r.details.get("auc", 0.0) for r in self.results]
        return (sum(auc_values) / len(auc_values)) * 100.0
