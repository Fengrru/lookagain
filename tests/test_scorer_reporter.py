"""Quick smoke test for scorer and reporter modules."""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lookagain.scenarios.base import TestResult
from lookagain.scorer import compute_mirage_score, aggregate_risk_categories
from lookagain.reporter import (
    print_terminal_report,
    generate_json_report,
    generate_markdown_report,
)

# Mock test results
mi_results = [
    TestResult("missing_001", "missing_image", True, "OK", "Counting"),
    TestResult("missing_002", "missing_image", True, "OK", "OCR"),
    TestResult(
        "missing_003", "missing_image", False, "Fabricated", "Object Recognition"
    ),
]
wi_results = [
    TestResult("wrong_001", "wrong_image", True, "OK", "Object Recognition"),
    TestResult(
        "wrong_002", "wrong_image", False, "Ignored image", "Scene Understanding"
    ),
]
corr_results = [
    TestResult("corr_001", "corruption", True, "Robust", "OCR", {"auc": 0.92}),
    TestResult(
        "corr_002", "corruption", True, "Robust", "Object Recognition", {"auc": 0.88}
    ),
]
tb_results = [
    TestResult("bias_001", "text_bias", True, "OK", "Object Recognition", {}, "image"),
    TestResult("bias_002", "text_bias", False, "Misled", "OCR", {}, "text"),
]

# Compute scores
score_data = compute_mirage_score(
    mi_results, wi_results, corr_results, tb_results, corruption_score=90.0
)
print(f"Mirage Score: {score_data['mirage_score']}")
print(f"Visual Reliance: {score_data['visual_reliance']}")
print(f"Missing Image Failure: {score_data['missing_image_failure']}%")
print(f"Wrong Image Failure: {score_data['wrong_image_failure']}%")
print(f"Corruption Robustness: {score_data['corruption_robustness']}%")
print(f"Text Bias Rate: {score_data['text_bias_rate']}%")

# Verify formula: 100 - (33.3*0.35 + 50*0.30 + (100-90)*0.15 + 50*0.20)
# = 100 - (11.67 + 15.0 + 1.5 + 10.0) = 100 - 38.17 = 61.8
expected = 100 - (100 / 3 * 0.35 + 50 * 0.30 + 10 * 0.15 + 50 * 0.20)
print(f"Expected Mirage Score: {expected:.1f}")
assert abs(score_data["mirage_score"] - expected) < 0.5, (
    f"Score mismatch: {score_data['mirage_score']} vs {expected:.1f}"
)
print("Score verification PASSED")

# Risk categories
all_results = mi_results + wi_results + corr_results + tb_results
risks = aggregate_risk_categories(all_results)
print(f"Risk categories: {risks}")
assert len(risks) == 3  # OCR(2), Object Recognition(1), Scene Understanding(1)
print("Risk categories PASSED")

# Test JSON report
with tempfile.TemporaryDirectory() as tmpdir:
    json_path = os.path.join(tmpdir, "report.json")
    generate_json_report("gpt-4o", score_data, risks, all_results, json_path)
    with open(json_path) as f:
        report = json.load(f)
    print(f"JSON report keys: {list(report.keys())}")
    print(f"JSON failures count: {len(report['failures'])}")
    assert len(report["failures"]) == 3
    print("JSON report PASSED")

    # Test Markdown report
    md_path = os.path.join(tmpdir, "report.md")
    generate_markdown_report("gpt-4o", score_data, risks, all_results, md_path)
    with open(md_path, encoding="utf-8") as f:
        content = f.read()
    print(f"Markdown report length: {len(content)} chars")
    assert "Mirage Score" in content
    print("Markdown report PASSED")

# Test terminal report (just ensure no crash)
print_terminal_report("gpt-4o", score_data, risks)
print("Terminal report PASSED")

print("\nAll scorer and reporter tests PASSED!")
