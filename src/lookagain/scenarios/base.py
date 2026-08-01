"""Base classes for test scenarios."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TestResult:
    """Result of a single test case."""

    __test__ = False  # Not a pytest test class

    test_id: str
    scenario: str  # "missing_image", "wrong_image", "corruption", "text_bias"
    passed: bool
    reason: str = ""
    risk_category: str = ""
    details: dict = field(default_factory=dict)
    trusts: str = ""  # for text_bias: "text", "image", or "uncertain"


class BaseScenario(ABC):
    """Abstract base for a test scenario.

    Each scenario runs a list of test cases against a VLM model,
    optionally using a Judge for answer evaluation.
    """

    def __init__(self, name: str):
        self.name = name
        self.results: list[TestResult] = []

    @abstractmethod
    def run(
        self,
        model,  # BaseVLMModel
        judge,  # BaseJudge | None
        test_cases: list[dict],
    ) -> list[TestResult]:
        """Run all test cases and return results."""
        ...

    @property
    def pass_rate(self) -> float:
        """Fraction of test cases that passed."""
        if not self.results:
            return 1.0
        passed = sum(1 for r in self.results if r.passed)
        return passed / len(self.results)

    @property
    def failure_rate(self) -> float:
        """Fraction of test cases that failed (0–100 scale)."""
        return (1.0 - self.pass_rate) * 100.0

    def risk_categories(self) -> dict[str, int]:
        """Count failures per risk category."""
        counts: dict[str, int] = {}
        for r in self.results:
            if not r.passed and r.risk_category:
                counts[r.risk_category] = counts.get(r.risk_category, 0) + 1
        return counts
