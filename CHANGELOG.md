# Changelog

All notable changes to LookAgain will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-08-02

### Added

- Anthropic and Gemini LLM-as-Judge adapters (`anthropic_judge.py`, `gemini_judge.py`)
- Configurable embedding settings (`embedding_config.py`)
- Configuration file support (YAML/TOML/JSON)
- Environment variable configuration
- Structured logging system
- Shared image loading utilities
- Dynamic test case counting for dry-run mode

### Fixed

- Missing image reference in wrong_image.json test cases
- Similarity threshold logic in WrongImage scenario
- Resource leak in embedding client (client caching)
- Data path resolution for package installations
- Dry-run mode hardcoded test case count

### Changed

- README installation instructions now prefer PyPI (`pip install lookagain`)
- Replaced duplicate `_load_image()` methods with shared utility function
- Improved error messages and logging output
- Updated documentation to professional standards

## [0.1.0] - 2026-07-31

### Added

- Initial release of LookAgain.
- Black-box VLM reliability auditing through API calls only.
- Four core test scenarios: Missing Image, Wrong Image, Image Corruption, and Text Bias.
- LookAgain Score: a 0–100 composite reliability rating with risk bands.
- Multi-provider support: OpenAI, Anthropic, Gemini, and OpenAI-compatible HTTP/local servers.
- LLM-as-Judge for nuanced cases, with rule-based fast paths.
- Terminal, JSON, and Markdown report formats.
- Synthetic test image generator (`data/generate_images.py`) so the benchmark runs out of the box.
- CLI entry point: `lookagain`.
- Smoke tests that do not require API keys.

---

## Versioning

We use [SemVer](https://semver.org/) for versioning. For the versions available, see the tags on this repository.

## How to Update This File

1. Add a new section under `[Unreleased]`
2. Follow the categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. Move items to the appropriate version when released
4. Add a new version header with the release date
