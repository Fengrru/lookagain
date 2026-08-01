"""Report generation: terminal table, JSON, Markdown."""

import json
import os
import sys

from .scenarios.base import TestResult
from .utils.logging_config import get_logger

logger = get_logger(__name__)


def _safe_marker(text: str) -> str:
    """Encode text safely for console output, falling back to ASCII."""
    try:
        text.encode(sys.stdout.encoding or "ascii")
        return text
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    # Fallback mappings for common emoji
    fallback = {
        "\u2705": "[OK]",
        "\u26a0\ufe0f": "[WARN]",
        "\U0001f534": "[FAIL]",
        "\u26a0": "[WARN]",
    }
    for emoji, ascii_val in fallback.items():
        text = text.replace(emoji, ascii_val)
    return text


def print_terminal_report(
    model_name: str,
    score_data: dict,
    risk_categories: dict[str, int],
) -> None:
    """Print a formatted terminal report."""
    ms = score_data["mirage_score"]
    vr = score_data["visual_reliance"]
    mif = score_data["missing_image_failure"]
    wif = score_data["wrong_image_failure"]
    cr = score_data["corruption_robustness"]
    tbr = score_data["text_bias_rate"]

    # Status markers (ASCII-safe)
    def marker(val: float, good_below: bool = True) -> str:
        if good_below:
            if val < 10:
                return "[OK]"
            elif val < 20:
                return "[WARN]"
            else:
                return "[FAIL]"
        else:
            if val > 85:
                return "[OK]"
            elif val > 70:
                return "[WARN]"
            else:
                return "[FAIL]"

    # Risk level
    if ms >= 85:
        risk_level = "[OK] LOW RISK"
    elif ms >= 60:
        risk_level = "[WARN] MODERATE RISK"
    else:
        risk_level = "[FAIL] HIGH RISK"

    # Top risk categories
    top_risks = list(risk_categories.items())[:3]
    risk_lines = (
        "\n".join(
            f"| {marker(c, good_below=False):6s} {cat:<20} ({c} failures) |"
            for cat, c in top_risks
        )
        if top_risks
        else "| (none detected)                               |"
    )

    sep = "+" + "-" * 42 + "+"
    report = f"""
{sep}
|          LookAgain Report              |
|          Model: {model_name:<28}|
|          LookAgain Score: {ms:<4.1f}/100        {risk_level:<20}|
{sep.replace("+", "|").replace("-", "-")}
| Visual Reliance        {vr:<5.1f}%    {marker(wif, good_below=True):6s} |
| Missing Image Failure  {mif:<5.1f}%    {marker(mif, good_below=True):6s} |
| Wrong Image Failure    {wif:<5.1f}%    {marker(wif, good_below=True):6s} |
| Corruption Robustness  {cr:<5.1f}%    {marker(100 - cr, good_below=True):6s} |
| Text Bias Rate         {tbr:<5.1f}%    {marker(tbr, good_below=True):6s} |
{sep.replace("+", "|").replace("-", "-")}
| High Risk Categories:                  |
{risk_lines}
{sep.replace("+", "|").replace("-", "-")}
| Detailed report: ./lookagain_report.md  |
{sep}
"""
    print(_safe_marker(report))


def generate_json_report(
    model_name: str,
    score_data: dict,
    risk_categories: dict[str, int],
    all_results: list[TestResult],
    output_path: str,
) -> None:
    """Generate a JSON report file."""
    report = {
        "model": model_name,
        "mirage_score": score_data["mirage_score"],
        "indicators": {
            "visual_reliance": score_data["visual_reliance"],
            "missing_image_failure": score_data["missing_image_failure"],
            "wrong_image_failure": score_data["wrong_image_failure"],
            "corruption_robustness": score_data["corruption_robustness"],
            "text_bias_rate": score_data["text_bias_rate"],
        },
        "sub_scores": score_data["sub_scores"],
        "risk_categories": risk_categories,
        "failures": [
            {
                "test_id": r.test_id,
                "scenario": r.scenario,
                "reason": r.reason,
                "risk_category": r.risk_category,
                "details": {
                    k: v
                    for k, v in r.details.items()
                    if isinstance(v, (str, int, float, bool, list))
                },
            }
            for r in all_results
            if not r.passed
        ],
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    logger.info(f"JSON report saved to {output_path}")


def generate_markdown_report(
    model_name: str,
    score_data: dict,
    risk_categories: dict[str, int],
    all_results: list[TestResult],
    output_path: str,
) -> None:
    """Generate a Markdown report file."""
    ms = score_data["mirage_score"]

    # Risk level
    if ms >= 85:
        risk_level = "✅ LOW RISK"
    elif ms >= 60:
        risk_level = "⚠️ MODERATE RISK"
    else:
        risk_level = "🔴 HIGH RISK"

    lines = [
        "# LookAgain Report",
        "",
        f"**Model:** `{model_name}`  ",
        f"**LookAgain Score:** {ms}/100 — {risk_level}",
        "",
        "## Summary",
        "",
        "| Indicator | Value | Status |",
        "|---|---|---|",
        f"| Visual Reliance | {score_data['visual_reliance']:.1f}% | |",
        f"| Missing Image Failure | {score_data['missing_image_failure']:.1f}% | |",
        f"| Wrong Image Failure | {score_data['wrong_image_failure']:.1f}% | |",
        f"| Corruption Robustness | {score_data['corruption_robustness']:.1f}% | |",
        f"| Text Bias Rate | {score_data['text_bias_rate']:.1f}% | |",
        "",
        "## High Risk Categories",
        "",
    ]

    for cat, count in list(risk_categories.items())[:5]:
        lines.append(f"- **{cat}**: {count} failures")

    lines.append("")
    lines.append("## Failure Details")
    lines.append("")

    failures = [r for r in all_results if not r.passed]
    if failures:
        for i, r in enumerate(failures[:20], 1):  # Cap at 20 for readability
            lines.append(f"### {i}. [{r.scenario}] {r.test_id}")
            lines.append(f"- **Risk Category:** {r.risk_category}")
            lines.append(f"- **Reason:** {r.reason}")
            q = r.details.get("question", "N/A")
            lines.append(f"- **Question:** {q}")
            a = r.details.get("answer", r.details.get("answer_correct", "N/A"))
            if isinstance(a, str) and len(a) > 200:
                a = a[:200] + "..."
            lines.append(f"- **Model Answer:** {a}")
            if r.trusts:
                lines.append(f"- **Trusts:** {r.trusts}")
            lines.append("")
    else:
        lines.append("No failures detected. 🎉")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by LookAgain — VLM Reliability Auditor*")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"Markdown report saved to {output_path}")
