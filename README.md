# Mirage Audit

**Mirage Audit** is a black-box reliability auditor for Vision-Language Models (VLMs). It tests whether your VLM truly relies on visual evidence, or whether it answers based on text bias, stereotypes, or hallucination when images are missing, corrupted, or misleading.

> Unlike training-based hallucination mitigators, Mirage Audit treats the model as a black box and only uses API calls. This makes it ideal for auditing commercial VLMs (OpenAI, Anthropic, Google Gemini) and local deployments alike.

## Why Mirage Audit?

Enterprises deploying VLMs face a hard question: *does this model actually look at the image, or is it just guessing from the prompt?* Mirage Audit answers this with standardized, reproducible tests and a single **Mirage Score**.

Use cases:
- **Pre-deployment validation** of VLM products.
- **Vendor comparison**: score GPT-4o, Claude, Gemini, and open-source VLMs on the same benchmark.
- **Regression testing** after model updates.
- **Compliance reporting** for AI risk frameworks (EU AI Act, NIST AI RMF).

## Test Scenarios

| Scenario | What it checks |
|---|---|
| **Missing Image** | Does the model abstain when no image is provided, or does it fabricate visual details? |
| **Wrong Image** | Does the answer change appropriately when the image is swapped for a semantically different one? |
| **Image Corruption** | Is the model robust to blur, noise, and occlusion? |
| **Text Bias** | Does misleading or suggestive text cause the model to ignore the image? |

The final **Mirage Score** combines these four dimensions into a 0–100 reliability rating with clear risk bands.

## Installation

```bash
# Basic install (OpenAI provider only)
pip install -e .

# With all commercial providers
pip install -e ".[all]"

# Individual providers
pip install -e ".[anthropic]"
pip install -e ".[gemini]"
```

## Quick Start

### 1. Generate synthetic test images

The built-in benchmark ships with image metadata but needs placeholder images to run. Generate them with:

```bash
python data/generate_images.py
```

This creates labeled synthetic images under `data/images/`. For production audits, replace these with real photographs or domain-specific images.

### 2. Set your API key

```bash
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export GOOGLE_API_KEY="..."
```

### 3. Run an audit

```bash
# OpenAI GPT-4o
mirage audit --provider openai --model gpt-4o

# Anthropic Claude
mirage audit --provider anthropic --model claude-3-5-sonnet-20241022

# Google Gemini
mirage audit --provider gemini --model gemini-1.5-flash

# Local vLLM / Ollama / LMDeploy (OpenAI-compatible endpoint)
mirage audit --provider http --model Qwen2-VL-7B-Instruct --base-url http://localhost:8000/v1
```

### 4. View reports

Reports are written to `./mirage_results/` by default in the formats you specify:

```bash
mirage audit --provider openai --model gpt-4o --format terminal,json,markdown
```

## CLI Reference

```bash
mirage audit \
  --provider openai \
  --model gpt-4o \
  --judge-provider openai \
  --judge gpt-4o \
  --output ./results \
  --format terminal,json,markdown \
  --data-dir ./my_test_cases
```

| Flag | Description |
|---|---|
| `--provider` | VLM provider: `openai`, `anthropic`, `gemini`, `http` |
| `--model` | Model identifier for the chosen provider |
| `--judge-provider` | Provider for the LLM-as-Judge (defaults to `--provider`) |
| `--judge` | Judge model identifier (defaults to `--model`) |
| `--base-url` | Base URL for HTTP/local providers |
| `--output` | Output directory for reports |
| `--format` | Comma-separated report formats |
| `--data-dir` | Custom test case directory |
| `--dry-run` | Estimate token usage and cost |
| `--api-key` | API key (overrides environment variable) |

## Project Structure

```
mirage-audit/
├── src/mirage_audit/
│   ├── cli.py                 # CLI entry point
│   ├── test_suite.py          # Orchestrates the four scenarios
│   ├── scorer.py              # Computes Mirage Score
│   ├── reporter.py            # terminal / json / markdown reports
│   ├── models/                # VLM adapters
│   │   ├── openai_model.py
│   │   ├── anthropic_model.py
│   │   ├── gemini_model.py
│   │   ├── http_model.py      # OpenAI-compatible local servers
│   │   └── factory.py
│   ├── judge/                 # LLM-as-Judge adapters
│   │   ├── openai_judge.py
│   │   └── factory.py
│   └── scenarios/             # Missing / Wrong / Corruption / Bias tests
├── data/
│   ├── generate_images.py     # Synthetic image generator
│   ├── images/                # Generated test images
│   └── test_cases/            # JSON test definitions
└── pyproject.toml
```

## Roadmap

- [x] Multi-provider support (OpenAI, Anthropic, Gemini, HTTP/local)
- [x] Built-in synthetic test images
- [ ] Web dashboard and PDF compliance reports
- [ ] Cost optimization: local lightweight judge, rule caching, stratified sampling
- [ ] Additional scenarios: adversarial images, multi-image, charts/tables, video frames
- [ ] Public leaderboard and open benchmark dataset

## License

MIT

## Contributing

Contributions are welcome. Please open an issue or pull request for new providers, scenarios, or reports.
