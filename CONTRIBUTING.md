# Contributing to LookAgain

Thank you for your interest in making LookAgain better! This document will help you get started.

## Ways to Contribute

- **Report bugs** by opening a GitHub issue with a minimal reproduction.
- **Suggest new scenarios** (e.g., adversarial images, multi-image, charts/tables, video frames).
- **Add provider support** for new VLM APIs or local inference servers.
- **Improve documentation**, examples, or tests.
- **Share benchmark results** to help us build a public leaderboard.

## Development Setup

```bash
git clone https://github.com/YOUR_ORG/lookagain.git
cd lookagain
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[all,dev]"
python data/generate_images.py
```

## Running Tests

```bash
pytest
```

The smoke tests do not require API keys. Provider-specific tests need the corresponding API key set in the environment.

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
ruff check src tests
ruff format --check src tests
```

Please keep formatting clean before opening a pull request.

## Adding a New Provider

1. Add a new adapter in `src/lookagain/models/` inheriting from `BaseVLMModel`.
2. Add a corresponding judge adapter if it differs from existing ones.
3. Register both in the factories (`src/lookagain/models/factory.py` and `src/lookagain/judge/factory.py`).
4. Add optional dependencies in `pyproject.toml`.
5. Update the README and CLI reference.
6. Add a minimal test if possible.

## Adding a New Scenario

1. Create a module under `src/lookagain/scenarios/`.
2. Implement a callable that accepts `(model, test_case, judge)` and returns a result dict with at least `passed` and `details`.
3. Add test cases under `data/test_cases/`.
4. Register the scenario in `src/lookagain/test_suite.py` and update `scorer.py` if the scoring logic changes.
5. Document the scenario in the README.

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Make your changes and add tests.
3. Ensure `pytest` and `ruff` pass.
4. Update the relevant documentation.
5. Open a pull request with a clear description and motivation.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
