"""Test case loading and orchestration.

Loads JSON test cases from files, runs all four scenarios,
and aggregates results.
"""

import json
import os
from typing import Dict, List, Optional

from .models.base import BaseVLMModel
from .judge.base import BaseJudge
from .scenarios.base import TestResult
from .scenarios.missing_image import MissingImageScenario
from .scenarios.wrong_image import WrongImageScenario
from .scenarios.corruption import CorruptionScenario
from .scenarios.text_bias import TextBiasScenario
from .scorer import compute_mirage_score, aggregate_risk_categories
from .reporter import (
    print_terminal_report,
    generate_json_report,
    generate_markdown_report,
)


def load_test_cases(data_dir: str) -> Dict[str, List[Dict]]:
    """Load all test case JSON files from data directory.

    Args:
        data_dir: Path to the test_cases directory.

    Returns:
        dict with keys "missing_image", "wrong_image", "corruption", "text_bias",
        each containing a list of test case dicts.
    """
    files = {
        "missing_image": os.path.join(data_dir, "missing_image.json"),
        "wrong_image": os.path.join(data_dir, "wrong_image.json"),
        "corruption": os.path.join(data_dir, "corruption.json"),
        "text_bias": os.path.join(data_dir, "text_bias.json"),
    }

    test_cases = {}
    for key, path in files.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                test_cases[key] = json.load(f)
        else:
            print(f"Warning: test case file not found: {path}")
            test_cases[key] = []

    return test_cases


def run_audit(
    model: BaseVLMModel,
    judge: Optional[BaseJudge],
    data_dir: str,
    output_dir: Optional[str] = None,
    formats: Optional[List[str]] = None,
) -> Dict:
    """Run the full LookAgain.

    Args:
        model: The VLM model to audit.
        judge: LLM-as-Judge for answer evaluation.
        data_dir: Path to test_cases directory.
        output_dir: Directory for report output files.
        formats: List of report formats: "terminal", "json", "markdown".

    Returns:
        dict with mirage_score and all sub-indicators.
    """
    if formats is None:
        formats = ["terminal"]

    # Load test cases
    print("Loading test cases...")
    test_cases = load_test_cases(data_dir)

    all_results: List[TestResult] = []

    # --- Scenario 1: Missing Image ---
    print("\n[1/4] Running Missing Image tests...")
    mi_scenario = MissingImageScenario()
    mi_results = mi_scenario.run(model, judge, test_cases.get("missing_image", []))
    all_results.extend(mi_results)
    mi_failed = sum(1 for r in mi_results if not r.passed)
    print(f"  {len(mi_results)} tests, {mi_failed} failed")

    # --- Scenario 2: Wrong Image ---
    print("\n[2/4] Running Wrong Image tests...")
    wi_scenario = WrongImageScenario()
    wi_results = wi_scenario.run(model, judge, test_cases.get("wrong_image", []))
    all_results.extend(wi_results)
    wi_failed = sum(1 for r in wi_results if not r.passed)
    print(f"  {len(wi_results)} tests, {wi_failed} failed")

    # --- Scenario 3: Image Corruption ---
    print("\n[3/4] Running Image Corruption tests...")
    corr_scenario = CorruptionScenario()
    corr_results = corr_scenario.run(model, judge, test_cases.get("corruption", []))
    all_results.extend(corr_results)
    corr_score = corr_scenario.corruption_score
    print(f"  {len(corr_results)} tests, robustness score: {corr_score:.1f}%")

    # --- Scenario 4: Text Bias ---
    print("\n[4/4] Running Text Bias tests...")
    tb_scenario = TextBiasScenario()
    tb_results = tb_scenario.run(model, judge, test_cases.get("text_bias", []))
    all_results.extend(tb_results)
    tb_failed = sum(1 for r in tb_results if not r.passed)
    print(f"  {len(tb_results)} tests, {tb_failed} failed")

    # Compute scores
    score_data = compute_mirage_score(
        missing_image_results=mi_results,
        wrong_image_results=wi_results,
        corruption_results=corr_results,
        text_bias_results=tb_results,
        corruption_score=corr_score,
    )

    risk_categories = aggregate_risk_categories(all_results)

    # Generate reports
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if "terminal" in formats:
        print_terminal_report(model.model_name, score_data, risk_categories)

    if "json" in formats and output_dir:
        json_path = os.path.join(output_dir, "mirage_report.json")
        generate_json_report(
            model.model_name, score_data, risk_categories, all_results, json_path
        )

    if "markdown" in formats and output_dir:
        md_path = os.path.join(output_dir, "mirage_report.md")
        generate_markdown_report(
            model.model_name, score_data, risk_categories, all_results, md_path
        )

    return score_data
