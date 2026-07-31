"""Test Missing Image scenario rule-based detection."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lookagain.scenarios.missing_image import MissingImageScenario

scenario = MissingImageScenario()

# Test rejection patterns (should detect as rejection)
rejection_answers = [
    "I cannot see the image you are referring to.",
    "I'm unable to view the picture, please provide one.",
    "No image was provided, so I cannot analyze visual content.",
    "I would need an image to answer that question.",
    "I don't see any photo attached to your message.",
    "Without an image, I cannot determine the answer.",
    "Unable to respond without the picture.",
]
for ans in rejection_answers:
    assert scenario._check_rejection(ans), f"Should detect rejection: {ans[:50]}..."
print(f"Rejection patterns: {len(rejection_answers)}/{len(rejection_answers)} passed")

# Test fabrication patterns (should detect as fabrication)
fabrication_answers = [
    "I can see a red car in the image.",
    "The image shows a group of people at a beach.",
    "In the picture, there appears to be a mountain range.",
    "There is a cat sitting on the table in the photo.",
    "It has three windows and a blue door.",
    "The image contains a text that says 'Welcome'.",
]
for ans in fabrication_answers:
    assert scenario._check_fabrication(ans), f"Should detect fabrication: {ans[:50]}..."
print(
    f"Fabrication patterns: {len(fabrication_answers)}/{len(fabrication_answers)} passed"
)

# Test neutral answers (neither clear rejection nor clear fabrication)
neutral_answers = [
    "That's an interesting question about the visual content.",
    "I'd be happy to help analyze images when provided.",
    "Visual analysis requires seeing the actual content.",
    "Without visual context, it's hard to be specific.",
]
for ans in neutral_answers:
    is_rej = scenario._check_rejection(ans)
    is_fab = scenario._check_fabrication(ans)
    # At least one should be false (or both false)
    # If both true, that's an ambiguous case that goes to judge
    print(f"  Neutral: rej={is_rej}, fab={is_fab} | {ans[:60]}...")

print("\nAll missing_image rule tests PASSED!")
