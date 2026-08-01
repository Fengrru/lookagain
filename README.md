<p align="center">
  <h1 align="center">LookAgain</h1>
  <p align="center">
    <strong>Black-box Reliability Auditor for Vision-Language Models</strong>
  </p>
  <p align="center">
    <a href="#installation">Installation</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#documentation">Documentation</a> •
    <a href="#contributing">Contributing</a> •
    <a href="#license">License</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.9+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen.svg" alt="License">
  <img src="https://img.shields.io/badge/status-alpha-orange.svg" alt="Status">
</p>

---

## What is LookAgain?

**LookAgain** is a black-box reliability auditor for Vision-Language Models (VLMs). It tests whether your VLM truly relies on visual evidence, or whether it answers based on text bias, stereotypes, or hallucination when images are missing, corrupted, or misleading.

> **Key Insight**: Unlike training-based hallucination mitigators, LookAgain treats the model as a black box and only uses API calls. This makes it ideal for auditing commercial VLMs (OpenAI, Anthropic, Google Gemini) and local deployments alike.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LookAgain Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐     ┌──────────────┐     ┌───────────────────┐    │
│  │   CLI   │────▶│ Model Adapter│────▶│  Test Scenarios   │    │
│  └─────────┘     └──────────────┘     └───────────────────┘    │
│       │                                       │                 │
│       │                                       ▼                 │
│       │                                ┌──────────────┐        │
│       │                                │    Scorer    │        │
│       │                                └──────────────┘        │
│       │                                       │                 │
│       │                                       ▼                 │
│       │                                ┌──────────────┐        │
│       └───────────────────────────────▶│   Reporter   │        │
│                                        └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Black-box Testing** | No access to model weights required -- API-only evaluation |
| **Comprehensive Scenarios** | 4 test dimensions covering visual reliance, robustness, and bias |
| **Multi-provider Support** | OpenAI, Anthropic, Google Gemini, and OpenAI-compatible endpoints |
| **Unified Scoring** | Single 0-100 LookAgain Score with clear risk bands |
| **LLM-as-Judge** | Optional AI-powered answer evaluation for nuanced cases |
| **Multiple Reports** | Terminal, JSON, and Markdown output formats |
| **Dry-run Mode** | Estimate token usage and costs before running tests |
| **Configurable** | YAML/TOML/JSON config files + environment variables |

---

## Why LookAgain?

Enterprises deploying VLMs face a hard question: *does this model actually look at the image, or is it just guessing from the prompt?* LookAgain answers this with standardized, reproducible tests.

### Use Cases

- **Pre-deployment Validation** -- Verify VLM products before production rollout
- **Vendor Comparison** -- Score GPT-4o, Claude, Gemini, and open-source VLMs on the same benchmark
- **Regression Testing** -- Detect performance degradation after model updates
- **Compliance Reporting** -- Generate evidence for EU AI Act, NIST AI RMF frameworks
- **Research Benchmarking** -- Standardized evaluation for academic papers

---

## Test Scenarios

| Scenario | What It Checks | How It Works |
|----------|----------------|--------------|
| **Missing Image** | Does the model abstain when no image is provided, or does it fabricate visual details? | Rule-based detection + LLM-as-Judge |
| **Wrong Image** | Does the answer change appropriately when the image is swapped? | Embedding similarity comparison |
| **Image Corruption** | Is the model robust to blur, noise, and occlusion? | Corruption robustness curve (AUC) |
| **Text Bias** | Does misleading text cause the model to ignore the image? | LLM-as-Judge evaluation |

### Test Scenarios Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Test Scenarios Overview                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Missing Image             Wrong Image           Image Corruption
│   ┌─────────────┐          ┌─────────────┐        ┌─────────────┐
│   │   No Image  │          │  Original   │        │  Original   │
│   │      ?      │          │     vs      │        │     +       │
│   │             │          │    Wrong    │        │  Corrupted  │
│   └─────────────┘          └─────────────┘        └─────────────┘
│         │                        │                       │
│         ▼                        ▼                       ▼
│   Fabrication              Similarity              Robustness
│   Detection                Comparison              Measurement
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                      Text Bias Test                             │
│                      ┌─────────────┐                            │
│                      │   Correct   │                            │
│                      │   Image +   │                            │
│                      │ Misleading  │                            │
│                      │    Text     │                            │
│                      └─────────────┘                            │
│                           │                                     │
│                           ▼                                     │
│                      Bias Detection                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### LookAgain Score

The final **LookAgain Score** (0-100) combines these four dimensions:

```
Score = 100 - (MissingImage * 0.35 + WrongImage * 0.30 + (100 - Corruption) * 0.15 + TextBias * 0.20)
```

| Score Range | Risk Level | Recommendation |
|-------------|------------|----------------|
| 85-100 | LOW RISK | Model shows strong visual reliance |
| 60-84 | MODERATE RISK | Some visual reliance issues detected |
| 0-59 | HIGH RISK | Significant visual reliance problems |

---

## Supported Providers

| Provider | Models | Auth Method |
|----------|--------|-------------|
| **OpenAI** | GPT-4o, GPT-4V, GPT-4o-mini | `OPENAI_API_KEY` |
| **Anthropic** | Claude 3 Opus, Claude 3.5 Sonnet | `ANTHROPIC_API_KEY` |
| **Google Gemini** | gemini-1.5-flash, gemini-1.5-pro | `GOOGLE_API_KEY` |
| **HTTP/Local** | Any OpenAI-compatible endpoint | Custom base URL |

---

## Installation

### From Source (Recommended)

```bash
git clone https://github.com/Fengrru/lookagain.git
cd lookagain
pip install -e .
```

### With All Providers

```bash
pip install -e ".[all]"
```

### Individual Providers

```bash
pip install -e ".[anthropic]"    # Anthropic Claude
pip install -e ".[gemini]"       # Google Gemini
```

### Requirements

- Python 3.9+
- OpenAI API key (for embedding similarity)
- Provider-specific API keys

---

## Quick Start

### 1. Generate Synthetic Test Images

```bash
python data/generate_images.py
```

### 2. Set Your API Key

```bash
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export GOOGLE_API_KEY="..."
```

### 3. Run an Audit

```bash
# OpenAI GPT-4o
lookagain audit --provider openai --model gpt-4o

# Anthropic Claude
lookagain audit --provider anthropic --model claude-3-5-sonnet-20241022

# Google Gemini
lookagain audit --provider gemini --model gemini-1.5-flash

# Local vLLM / Ollama
lookagain audit --provider http --model Qwen2-VL-7B-Instruct --base-url http://localhost:8000/v1
```

### 4. Example Output

```
$ lookagain audit --provider openai --model gpt-4o

LookAgain
  Provider:         openai
  Model under test: gpt-4o
  Judge provider:   openai
  Judge:            gpt-4o
  Output:           ./lookagain_results
  Formats:          ['terminal', 'json', 'markdown']

Loading test cases...
[1/4] Running Missing Image tests...
  12 tests, 2 failed
[2/4] Running Wrong Image tests...
  14 tests, 3 failed
[3/4] Running Image Corruption tests...
  12 tests, robustness score: 85.2%
[4/4] Running Text Bias tests...
  12 tests, 4 failed

+------------------------------------------+
|          LookAgain Report                |
|          Model: gpt-4o                   |
|          LookAgain Score: 72.5/100       |
|          MODERATE RISK                   |
+------------------------------------------+

Audit complete. LookAgain Score: 72.5/100
```

### 5. View Reports

Reports are saved to `./lookagain_results/`:

```
lookagain_results/
├── lookagain_report.json      # Machine-readable results
└── lookagain_report.md        # Human-readable summary
```

---

## Configuration

LookAgain supports configuration via files or environment variables.

### Configuration File

Create `.lookagain.yaml` in your project root:

```yaml
model:
  provider: openai
  model: gpt-4o

judge:
  provider: openai
  model: gpt-4o

output:
  directory: ./lookagain_results
  formats:
    - terminal
    - json
    - markdown

logging:
  level: INFO
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOOKAGAIN_PROVIDER` | Model provider | `openai` |
| `LOOKAGAIN_MODEL` | Model name | `gpt-4o` |
| `LOOKAGAIN_API_KEY` | API key | Provider-specific |
| `LOOKAGAIN_HTTP_BASE_URL` | HTTP provider base URL | -- |
| `LOOKAGAIN_OUTPUT_DIR` | Output directory | `./lookagain_results` |
| `LOOKAGAIN_LOG_LEVEL` | Logging level | `INFO` |

---

## CLI Reference

```bash
lookagain audit [OPTIONS]
```

| Flag | Description | Default |
|------|-------------|---------|
| `--provider` | VLM provider (`openai`, `anthropic`, `gemini`, `http`) | `openai` |
| `--model` | Model identifier | `gpt-4o` |
| `--judge-provider` | Judge provider | Same as `--provider` |
| `--judge` | Judge model | Same as `--model` |
| `--base-url` | Base URL for HTTP providers | -- |
| `--output` | Output directory | `./lookagain_results` |
| `--format` | Report formats (comma-separated) | `terminal,json,markdown` |
| `--data-dir` | Custom test cases directory | Built-in |
| `--dry-run` | Estimate token usage | -- |
| `--api-key` | API key (overrides env var) | -- |
| `--config` | Config file path | `.lookagain.yaml` |

---

## Project Structure

```
lookagain/
├── src/lookagain/
│   ├── __init__.py
│   ├── cli.py                    # CLI entry point
│   ├── config.py                 # Configuration management
│   ├── test_suite.py             # Audit orchestration
│   ├── scorer.py                 # LookAgain Score computation
│   ├── reporter.py               # Report generation
│   ├── models/                   # VLM adapters
│   │   ├── base.py               # Abstract base class
│   │   ├── openai_model.py       # OpenAI adapter
│   │   ├── anthropic_model.py    # Anthropic adapter
│   │   ├── gemini_model.py       # Google Gemini adapter
│   │   ├── http_model.py         # OpenAI-compatible endpoints
│   │   └── factory.py            # Model factory
│   ├── judge/                    # LLM-as-Judge adapters
│   │   ├── base.py               # Abstract base class
│   │   ├── openai_judge.py       # OpenAI Judge
│   │   ├── prompts.py            # Judge prompt templates
│   │   └── factory.py            # Judge factory
│   ├── scenarios/                # Test scenarios
│   │   ├── base.py               # Base scenario + TestResult
│   │   ├── missing_image.py      # Missing Image test
│   │   ├── wrong_image.py        # Wrong Image test
│   │   ├── corruption.py         # Image Corruption test
│   │   └── text_bias.py          # Text Bias test
│   └── utils/
│       ├── embedding.py          # Text embedding similarity
│       ├── image_utils.py        # Image corruption utilities
│       └── logging_config.py     # Logging configuration
├── data/
│   ├── generate_images.py        # Synthetic image generator
│   ├── images/                   # Generated test images
│   └── test_cases/               # JSON test definitions
├── tests/
│   ├── test_smoke.py             # Smoke tests
│   └── test_scorer_reporter.py   # Scorer/reporter tests
├── .lookagain.yaml               # Example config
├── pyproject.toml                # Project metadata
└── README.md
```

---

## Custom Test Cases

Create custom test cases in JSON format:

```json
[
  {
    "id": "custom_001",
    "question": "What animal is in this image?",
    "risk_category": "Object Recognition",
    "image_path": "images/my_test.jpg",
    "ground_truth": "A golden retriever dog"
  }
]
```

Run with custom test cases:

```bash
lookagain audit --provider openai --model gpt-4o --data-dir ./my_test_cases
```

---

## Development

### Setup Development Environment

```bash
git clone https://github.com/Fengrru/lookagain.git
cd lookagain
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Linting
ruff check src/

# Formatting
ruff format src/
```

---

## Roadmap

- [x] Multi-provider support (OpenAI, Anthropic, Gemini, HTTP/local)
- [x] Built-in synthetic test images
- [x] Configuration file support
- [x] Structured logging
- [ ] Web dashboard and PDF compliance reports
- [ ] Cost optimization: local lightweight judge, rule caching
- [ ] Additional scenarios: adversarial images, multi-image, charts, video frames
- [ ] Async/parallel execution support
- [ ] Public leaderboard and open benchmark dataset

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- New VLM provider adapters
- Additional test scenarios
- Judge implementations (Anthropic, Gemini native)
- Documentation improvements
- Bug fixes and tests

---

## Citation

If you use LookAgain in your research, please cite:

```bibtex
@software{lookagain2024,
  title={LookAgain: Black-box Reliability Auditor for Vision-Language Models},
  author={Fengrru},
  year={2024},
  version={0.1.0},
  url={https://github.com/Fengrru/lookagain}
}
```

---

## License

This project is licensed under the MIT License -- see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built with inspiration from [VLMEvalKit](https://github.com/open-compass/VLMEvalKit) and [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)
- Uses [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), and [Google](https://ai.google.dev/) APIs for model evaluation
