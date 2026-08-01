"""LookAgain Score calculator.

Weighted composite score from four sub-indicators:
  LookAgain Score = 100 - (MissingImageFailure × 0.35
                         + WrongImageFailure  × 0.30
                         + (100 - CorruptionScore) × 0.15
                         + TextBiasRate       × 0.20)

All sub-indicators are on 0–100 scale (higher = worse).
LookAgain Score is on 0–100 scale (higher = better).
"""

from .scenarios.base import TestResult

# Weights for each sub-indicator (must sum to 1.0)
WEIGHTS = {
    "missing_image": 0.35,
    "wrong_image": 0.30,
    "corruption": 0.15,
    "text_bias": 0.20,
}


def compute_mirage_score(
    missing_image_results: list[TestResult],
    wrong_image_results: list[TestResult],
    corruption_results: list[TestResult],
    text_bias_results: list[TestResult],
    corruption_score: float,  # 0–100, from CorruptionScenario.corruption_score
) -> dict:
    """Compute the composite LookAgain Score and sub-indicators.

    Args:
        missing_image_results: Results from MissingImageScenario.
        wrong_image_results: Results from WrongImageScenario.
        corruption_results: Results from CorruptionScenario.
        text_bias_results: Results from TextBiasScenario.
        corruption_score: Pre-computed corruption robustness score (0–100).

    Returns:
        dict with keys: mirage_score (LookAgain Score), visual_reliance,
                       missing_image_failure, wrong_image_failure,
                       corruption_robustness, text_bias_rate, sub_scores
    """
    # Sub-indicators (0–100, higher = worse, except corruption)
    missing_image_failure = _failure_rate(missing_image_results)
    wrong_image_failure = _failure_rate(wrong_image_results)
    text_bias_rate = _failure_rate(text_bias_results)
    corruption_robustness = corruption_score  # 0–100, higher = better

    # Composite score
    penalty = (
        missing_image_failure * WEIGHTS["missing_image"]
        + wrong_image_failure * WEIGHTS["wrong_image"]
        + (100.0 - corruption_robustness) * WEIGHTS["corruption"]
        + text_bias_rate * WEIGHTS["text_bias"]
    )

    mirage_score = max(0.0, min(100.0, 100.0 - penalty))

    # Visual Reliance = 100 - (MissingImageFailure * 0.4 + WrongImageFailure * 0.6)
    visual_reliance = max(
        0.0, 100.0 - (missing_image_failure * 0.4 + wrong_image_failure * 0.6)
    )

    return {
        "mirage_score": round(mirage_score, 1),
        "visual_reliance": round(visual_reliance, 1),
        "missing_image_failure": round(missing_image_failure, 1),
        "wrong_image_failure": round(wrong_image_failure, 1),
        "corruption_robustness": round(corruption_robustness, 1),
        "text_bias_rate": round(text_bias_rate, 1),
        "sub_scores": {
            "missing_image": {
                "failure_rate": round(missing_image_failure, 1),
                "total": len(missing_image_results),
                "passed": sum(1 for r in missing_image_results if r.passed),
                "failed": sum(1 for r in missing_image_results if not r.passed),
            },
            "wrong_image": {
                "failure_rate": round(wrong_image_failure, 1),
                "total": len(wrong_image_results),
                "passed": sum(1 for r in wrong_image_results if r.passed),
                "failed": sum(1 for r in wrong_image_results if not r.passed),
            },
            "corruption": {
                "robustness": round(corruption_robustness, 1),
                "total": len(corruption_results),
            },
            "text_bias": {
                "failure_rate": round(text_bias_rate, 1),
                "total": len(text_bias_results),
                "passed": sum(1 for r in text_bias_results if r.passed),
                "failed": sum(1 for r in text_bias_results if not r.passed),
            },
        },
    }


def aggregate_risk_categories(all_results: list[TestResult]) -> dict[str, int]:
    """Count failures per risk category across all scenarios.

    Args:
        all_results: Combined list of TestResult from all scenarios.

    Returns:
        dict mapping risk_category → failure_count, sorted descending.
    """
    counts: dict[str, int] = {}
    for r in all_results:
        if not r.passed and r.risk_category:
            counts[r.risk_category] = counts.get(r.risk_category, 0) + 1

    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def _failure_rate(results: list[TestResult]) -> float:
    """Compute failure rate as percentage (0–100)."""
    if not results:
        return 0.0
    failed = sum(1 for r in results if not r.passed)
    return (failed / len(results)) * 100.0
