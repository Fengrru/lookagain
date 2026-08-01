"""Four test scenarios: Missing Image, Wrong Image, Corruption, Text Bias."""

from .base import BaseScenario, TestResult
from .corruption import CorruptionScenario
from .missing_image import MissingImageScenario
from .text_bias import TextBiasScenario
from .wrong_image import WrongImageScenario

__all__ = [
    "BaseScenario",
    "TestResult",
    "MissingImageScenario",
    "WrongImageScenario",
    "CorruptionScenario",
    "TextBiasScenario",
]
