"""Tests for scorer and reporter modules."""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lookagain.reporter import (
    generate_json_report,
    generate_markdown_report,
    print_terminal_report,
)
from lookagain.scenarios.base import TestResult
from lookagain.scorer import aggregate_risk_categories, compute_lookagain_score


# --- Fixtures ---

@pytest.fixture
def mi_results():
    return [
        TestResult("missing_001", "missing_image", True, "OK", "Counting"),
        TestResult("missing_002", "missing_image", True, "OK", "OCR"),
        TestResult(
            "missing_003", "missing_image", False, "Fabricated", "Object Recognition"
        ),
    ]


@pytest.fixture
def wi_results():
    return [
        TestResult("wrong_001", "wrong_image", True, "OK", "Object Recognition"),
        TestResult(
            "wrong_002", "wrong_image", False, "Ignored image", "Scene Understanding"
        ),
    ]


@pytest.fixture
def corr_results():
    return [
        TestResult("corr_001", "corruption", True, "Robust", "OCR", {"auc": 0.92}),
        TestResult(
            "corr_002", "corruption", True, "Robust", "Object Recognition", {"auc": 0.88}
        ),
    ]


@pytest.fixture
def tb_results():
    return [
        TestResult("bias_001", "text_bias", True, "OK", "Object Recognition", {}, "image"),
        TestResult("bias_002", "text_bias", False, "Misled", "OCR", {}, "text"),
    ]


@pytest.fixture
def all_results(mi_results, wi_results, corr_results, tb_results):
    return mi_results + wi_results + corr_results + tb_results


@pytest.fixture
def score_data(mi_results, wi_results, corr_results, tb_results):
    return compute_lookagain_score(
        mi_results, wi_results, corr_results, tb_results, corruption_score=90.0
    )


@pytest.fixture
def risk_categories(all_results):
    return aggregate_risk_categories(all_results)


# --- Tests ---

class TestScorer:
    """Tests for the scorer module."""

    def test_score_value(self, score_data):
        """Verify LookAgain Score matches expected formula output."""
        # Formula: 100 - (33.3*0.35 + 50*0.30 + (100-90)*0.15 + 50*0.20)
        # = 100 - (11.67 + 15.0 + 1.5 + 10.0) = 100 - 38.17 = 61.8
        expected = 100 - (100 / 3 * 0.35 + 50 * 0.30 + 10 * 0.15 + 50 * 0.20)
        assert abs(score_data["lookagain_score"] - expected) < 0.5, (
            f"Score mismatch: {score_data['lookagain_score']} vs {expected:.1f}"
        )

    def test_score_in_range(self, score_data):
        assert 0 <= score_data["lookagain_score"] <= 100

    def test_sub_indicators_present(self, score_data):
        for key in (
            "visual_reliance",
            "missing_image_failure",
            "wrong_image_failure",
            "corruption_robustness",
            "text_bias_rate",
        ):
            assert key in score_data

    def test_sub_scores_keys(self, score_data):
        for key in ("missing_image", "wrong_image", "corruption", "text_bias"):
            assert key in score_data["sub_scores"]

    def test_risk_categories(self, risk_categories):
        """Verify risk category aggregation."""
        assert len(risk_categories) == 3
        # OCR has 2 failures (corr + bias), Object Recognition 1, Scene Understanding 1
        # But corr_001 and corr_002 passed, so only bias_002 is a failure for OCR
        # missing_003 (Object Recognition), wrong_002 (Scene Understanding), bias_002 (OCR)
        # Total: 3 categories
        assert risk_categories["OCR"] == 1
        assert risk_categories["Object Recognition"] == 1
        assert risk_categories["Scene Understanding"] == 1


class TestReporter:
    """Tests for the reporter module."""

    def test_json_report(self, score_data, risk_categories, all_results):
        """Test JSON report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "report.json")
            generate_json_report(
                "gpt-4o", score_data, risk_categories, all_results, json_path
            )
            with open(json_path) as f:
                report = json.load(f)

            assert "lookagain_score" in report
            assert "indicators" in report
            assert "sub_scores" in report
            assert "failures" in report
            assert len(report["failures"]) == 3

    def test_markdown_report(self, score_data, risk_categories, all_results):
        """Test Markdown report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = os.path.join(tmpdir, "report.md")
            generate_markdown_report(
                "gpt-4o", score_data, risk_categories, all_results, md_path
            )
            with open(md_path, encoding="utf-8") as f:
                content = f.read()

            assert "LookAgain Report" in content
            assert "LookAgain Score" in content
            assert "Summary" in content

    def test_terminal_report(self, score_data, risk_categories):
        """Test terminal report doesn't crash."""
        # Should not raise any exception
        print_terminal_report("gpt-4o", score_data, risk_categories)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
