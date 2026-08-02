"""Test Missing Image scenario rule-based detection."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lookagain.scenarios.missing_image import MissingImageScenario

scenario = MissingImageScenario()

# Test data
REJECTION_ANSWERS = [
    "I cannot see the image you are referring to.",
    "I'm unable to view the picture, please provide one.",
    "No image was provided, so I cannot analyze visual content.",
    "I would need an image to answer that question.",
    "I don't see any photo attached to your message.",
    "Without an image, I cannot determine the answer.",
    "Unable to respond without the picture.",
]

FABRICATION_ANSWERS = [
    "I can see a red car in the image.",
    "The image shows a group of people at a beach.",
    "In the picture, there appears to be a mountain range.",
    "There is a cat sitting on the table in the photo.",
    "It has three windows and a blue door.",
    "The image contains a text that says 'Welcome'.",
]

NEUTRAL_ANSWERS = [
    "That's an interesting question about the visual content.",
    "I'd be happy to help analyze images when provided.",
    "Visual analysis requires seeing the actual content.",
    "Without visual context, it's hard to be specific.",
]


class TestRejectionPatterns:
    """Tests for rejection pattern detection."""

    @pytest.mark.parametrize("answer", REJECTION_ANSWERS)
    def test_detects_rejection(self, answer):
        assert scenario._check_rejection(answer), (
            f"Should detect rejection: {answer[:50]}..."
        )


class TestFabricationPatterns:
    """Tests for fabrication pattern detection."""

    @pytest.mark.parametrize("answer", FABRICATION_ANSWERS)
    def test_detects_fabrication(self, answer):
        assert scenario._check_fabrication(answer), (
            f"Should detect fabrication: {answer[:50]}..."
        )


class TestNeutralAnswers:
    """Tests for neutral answers that should be ambiguous."""

    @pytest.mark.parametrize("answer", NEUTRAL_ANSWERS)
    def test_neither_or_both(self, answer):
        """Neutral answers should not be clearly rejection or fabrication."""
        is_rej = scenario._check_rejection(answer)
        is_fab = scenario._check_fabrication(answer)
        # At least one should be false (or both false)
        assert not (is_rej and is_fab), (
            f"Both detected for: {answer[:60]}..."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
