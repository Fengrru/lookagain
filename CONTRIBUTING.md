# Contributing to LookAgain

Thank you for your interest in making LookAgain better! This document will help you get started.

## Ways to Contribute

- **Report bugs** — Open a GitHub issue with a minimal reproduction
- **Suggest new scenarios** — Adversarial images, multi-image, charts/tables, video frames
- **Add provider support** — New VLM APIs or local inference servers
- **Improve documentation** — Examples, tutorials, or API docs
- **Share benchmark results** — Help build our public leaderboard
- **Submit code fixes** — Check open issues for "good first issue" labels

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- API key for at least one provider (OpenAI recommended for testing)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/lookagain.git
cd lookagain

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with all dependencies
pip install -e ".[all,dev]"

# Generate synthetic test images
python data/generate_images.py
```

### Verify Setup

```bash
# Run smoke tests (no API key required)
pytest tests/test_smoke.py -v

# Check code quality
ruff check src tests
ruff format --check src tests
```

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

### Formatting Rules

- Follow PEP 8 style guidelines
- Use type hints for all public functions
- Write docstrings for classes and public methods
- Keep functions focused and under 50 lines when possible

### Commands

```bash
# Lint
ruff check src tests

# Format
ruff format src tests

# Check formatting
ruff format --check src tests
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_smoke.py -v

# Run with coverage
pytest --cov=lookagain tests/
```

### Test Types

| Type | Description | API Key Required |
|------|-------------|------------------|
| `test_smoke.py` | Core functionality tests | No |
| `test_scorer_reporter.py` | Score computation and reporting | No |
| Provider tests | Provider-specific integration tests | Yes |

### Writing Tests

- Add tests for new features or bug fixes
- Use descriptive test names
- Mock external API calls when possible
- Test both success and error paths

## Adding a New Provider

### Step-by-Step Guide

1. **Create the adapter** in `src/lookagain/models/`:

```python
from .base import BaseVLMModel

class NewProviderModel(BaseVLMModel):
    def __init__(self, model_name: str, api_key: str = None):
        super().__init__(model_name)
        # Initialize your client here

    def generate(self, image: Image.Image, prompt: str) -> str:
        # Implement your API call here
        pass
```

2. **Register in factory** (`src/lookagain/models/factory.py`):

```python
PROVIDERS = {
    "new_provider": NewProviderModel,
    # ... existing providers
}
```

3. **Add optional dependency** in `pyproject.toml`:

```toml
[project.optional-dependencies]
new_provider = ["new-provider-sdk>=1.0"]
```

4. **Add tests** in `tests/`

5. **Update documentation** in README.md

## Adding a New Scenario

### Step-by-Step Guide

1. **Create the scenario** in `src/lookagain/scenarios/`:

```python
from .base import BaseScenario, TestResult

class NewScenario(BaseScenario):
    def __init__(self):
        super().__init__("new_scenario")

    def run(self, model, judge, test_cases: List[Dict]) -> List[TestResult]:
        results = []
        for tc in test_cases:
            # Implement your test logic
            results.append(TestResult(
                test_id=tc["id"],
                scenario="new_scenario",
                passed=True,  # or False
                reason="...",
                risk_category=tc.get("risk_category", ""),
            ))
        return results
```

2. **Add test cases** in `data/test_cases/new_scenario.json`

3. **Register in orchestration** (`src/lookagain/test_suite.py`)

4. **Update scoring** (`src/lookagain/scorer.py`) if needed

5. **Document** in README.md

## Pull Request Process

### Before Submitting

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add or update tests
5. Run quality checks:
   ```bash
   pytest
   ruff check src tests
   ruff format --check src tests
   ```
6. Update documentation if needed

### PR Guidelines

- Write a clear, descriptive title
- Reference any related issues
- Include a summary of changes
- Add screenshots for UI changes (if applicable)
- Ensure CI passes

### Review Process

- Maintainers will review your PR within 7 days
- Address any feedback promptly
- Once approved, a maintainer will merge your PR

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a release tag: `git tag v0.1.0`
4. Push to GitHub: `git push origin main --tags`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open a GitHub issue for bugs or feature requests
- Start a discussion for general questions
- Check existing issues before creating new ones

Thank you for contributing! 🎉
