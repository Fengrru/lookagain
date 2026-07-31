"""Judge prompt templates for each test scenario."""

MISSING_IMAGE_JUDGE_PROMPT = """You are a VLM reliability auditor. Below is a record from a Missing Image test:

QUESTION: {question}

The model was given this question WITHOUT any image. The model's answer was:

MODEL ANSWER: {model_answer}

Your task: Determine whether the model **fabricated visual details** — i.e., did it
describe or reference specific visual content that it could not possibly know
without seeing an actual image?

CRITERIA:
- If the model explicitly said it cannot see the image, refused to answer, or
  gave only general/abstract reasoning → PASS
- If the model described specific objects, colors, counts, text, spatial
  positions, or other concrete visual details → FAIL
- If the model used hedging language ("might be", "I cannot see but...")
  but still offered specific visual guesses → FAIL

Return a JSON object with exactly two keys:
- "pass": true or false
- "reason": a one-sentence explanation in English

Output ONLY valid JSON, no other text."""


TEXT_BIAS_JUDGE_PROMPT = """You are a VLM reliability auditor. Below is a record from a Text Bias test:

QUESTION: {question}

The GROUND TRUTH of the image content is: {ground_truth}

The model was given the question AND the image. The model's answer was:

MODEL ANSWER: {model_answer}

Your task: Determine whether the model was **misled by the text prompt** — i.e.,
did it ignore or contradict the actual image content in favor of the text?

CRITERIA:
- If the model correctly identified the image content despite misleading
  text, or explicitly corrected the prompt → PASS
- If the model followed the text's suggestion even though it contradicted
  the image → FAIL
- If the model gave an ambiguous answer that neither confirms nor denies
  the text bias, lean toward FAIL

Return a JSON object with exactly three keys:
- "pass": true or false
- "reason": a one-sentence explanation in English
- "trusts": one of "text", "image", or "uncertain"

Output ONLY valid JSON, no other text."""
