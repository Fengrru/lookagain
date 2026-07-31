# Changelog

All notable changes to Mirage Audit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-31

### Added

- Initial release of Mirage Audit.
- Black-box VLM reliability auditing through API calls only.
- Four core test scenarios: Missing Image, Wrong Image, Image Corruption, and Text Bias.
- Mirage Score: a 0–100 composite reliability rating with risk bands.
- Multi-provider support: OpenAI, Anthropic, Gemini, and OpenAI-compatible HTTP/local servers.
- LLM-as-Judge for nuanced cases, with rule-based fast paths.
- Terminal, JSON, and Markdown report formats.
- Synthetic test image generator (`data/generate_images.py`) so the benchmark runs out of the box.
- CLI entry point: `mirage audit`.
- Smoke tests that do not require API keys.
