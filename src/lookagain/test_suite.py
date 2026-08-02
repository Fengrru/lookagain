"""Test case loading and orchestration.

Loads JSON test cases from files, runs all four scenarios,
and aggregates results.
"""

import json
import os
from typing import Optional

from .judge.base import BaseJudge
from .models.base import BaseVLMModel
from .reporter import (
    generate_json_report,
    generate_markdown_report,
    print_terminal_report,
)
from .scenarios.base import TestResult
from .scenarios.corruption import CorruptionScenario
from .scenarios.missing_image import MissingImageScenario
from .scenarios.text_bias import TextBiasScenario
from .scenarios.wrong_image import WrongImageScenario
from .scorer import aggregate_risk_categories, compute_lookagain_score
from .utils.logging_config import get_logger

logger = get_logger(__name__)


def load_test_cases(data_dir: str) -> dict[str, list[dict]]:
    """Load all test case JSON files from data directory.

    Image paths in the JSON files are relative to the parent of ``data_dir``
    (e.g. ``images/wrong/cat.jpg`` resolves to ``<parent>/images/wrong/cat.jpg``).
    This function converts them to absolute paths so that scenarios can load
    images regardless of the current working directory.

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

    # Image paths in JSON are relative to the parent of data_dir
    # (e.g. data_dir = .../data/test_cases -> images live in .../data/images)
    image_base = os.path.dirname(data_dir)  # .../data

    test_cases = {}
    for key, path in files.items():
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cases = json.load(f)
                # Resolve relative image paths to absolute
                for tc in cases:
                    _resolve_image_paths(tc, image_base)
                test_cases[key] = cases
        else:
            logger.warning(f"Test case file not found: {path}")
            test_cases[key] = []

    return test_cases


def _resolve_image_paths(tc: dict, base_dir: str) -> None:
    """Convert relative image paths in a test case to absolute paths.

    Handles keys: image_path, correct_image_path, wrong_image_paths.

    Args:
        tc: Test case dict (modified in place).
        base_dir: Base directory for resolving relative paths.
    """
    path_keys = ["image_path", "correct_image_path"]
    for key in path_keys:
        val = tc.get(key, "")
        if val and not os.path.isabs(val):
            tc[key] = os.path.join(base_dir, val)

    wrong_paths = tc.get("wrong_image_paths", [])
    if wrong_paths:
        tc["wrong_image_paths"] = [
            os.path.join(base_dir, p) if not os.path.isabs(p) else p
            for p in wrong_paths
        ]


def run_audit(
    model: BaseVLMModel,
    judge: Optional[BaseJudge],
    data_dir: str,
    output_dir: Optional[str] = None,
    formats: Optional[list[str]] = None,
) -> dict:
    """Run the full LookAgain.

    Args:
        model: The VLM model to audit.
        judge: LLM-as-Judge for answer evaluation.
        data_dir: Path to test_cases directory.
        output_dir: Directory for report output files.
        formats: List of report formats: "terminal", "json", "markdown".

    Returns:
        dict with lookagain_score and all sub-indicators.
    """
    if formats is None:
        formats = ["terminal"]

    # Load test cases
    logger.info("Loading test cases...")
    test_cases = load_test_cases(data_dir)

    all_results: list[TestResult] = []

    # --- Scenario 1: Missing Image ---
    logger.info("[1/4] Running Missing Image tests...")
    mi_scenario = MissingImageScenario()
    mi_results = mi_scenario.run(model, judge, test_cases.get("missing_image", []))
    all_results.extend(mi_results)
    mi_failed = sum(1 for r in mi_results if not r.passed)
    logger.info(f"  {len(mi_results)} tests, {mi_failed} failed")

    # --- Scenario 2: Wrong Image ---
    logger.info("[2/4] Running Wrong Image tests...")
    wi_scenario = WrongImageScenario()
    wi_results = wi_scenario.run(model, judge, test_cases.get("wrong_image", []))
    all_results.extend(wi_results)
    wi_failed = sum(1 for r in wi_results if not r.passed)
    logger.info(f"  {len(wi_results)} tests, {wi_failed} failed")

    # --- Scenario 3: Image Corruption ---
    logger.info("[3/4] Running Image Corruption tests...")
    corr_scenario = CorruptionScenario()
    corr_results = corr_scenario.run(model, judge, test_cases.get("corruption", []))
    all_results.extend(corr_results)
    corr_score = corr_scenario.corruption_score
    logger.info(f"  {len(corr_results)} tests, robustness score: {corr_score:.1f}%")

    # --- Scenario 4: Text Bias ---
    logger.info("[4/4] Running Text Bias tests...")
    tb_scenario = TextBiasScenario()
    tb_results = tb_scenario.run(model, judge, test_cases.get("text_bias", []))
    all_results.extend(tb_results)
    tb_failed = sum(1 for r in tb_results if not r.passed)
    logger.info(f"  {len(tb_results)} tests, {tb_failed} failed")

    # Compute scores
    score_data = compute_lookagain_score(
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
        json_path = os.path.join(output_dir, "lookagain_report.json")
        generate_json_report(
            model.model_name, score_data, risk_categories, all_results, json_path
        )

    if "markdown" in formats and output_dir:
        md_path = os.path.join(output_dir, "lookagain_report.md")
        generate_markdown_report(
            model.model_name, score_data, risk_categories, all_results, md_path
        )

    return score_data
