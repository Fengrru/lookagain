"""CLI entry point for LookAgain.

Usage:
    LookAgain --provider openai --model gpt-4o
    LookAgain --provider anthropic --model claude-3-5-sonnet-20241022
    LookAgain --provider gemini --model gemini-1.5-flash
    LookAgain --provider http --model Qwen2-VL-7B-Instruct --base-url http://localhost:8000/v1
    LookAgain --provider openai --model gpt-4o --judge-provider openai --judge gpt-4o
"""

import argparse
import os
import sys

from lookagain.models.factory import list_providers as list_model_providers
from lookagain.utils.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LookAgain: VLM Reliability Auditor")

    subparsers = parser.add_subparsers(dest="command")
    _add_audit_parser(subparsers)
    return parser


def _add_audit_parser(subparsers):
    providers = ", ".join(list_model_providers())

    p = subparsers.add_parser(
        "audit",
        help="Run VLM reliability audit",
        description="Audit a VLM for visual evidence reliance across 4 test scenarios.",
    )
    p.add_argument(
        "--provider",
        type=str,
        default=None,
        help=f"VLM provider (default: openai). Supported: {providers}",
    )
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help="VLM model to audit (default: gpt-4o)",
    )
    p.add_argument(
        "--judge-provider",
        type=str,
        default=None,
        help="Judge provider (defaults to --provider)",
    )
    p.add_argument(
        "--judge",
        type=str,
        default=None,
        help="Judge model for answer evaluation (default: same as --model)",
    )
    p.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Base URL for HTTP/local provider (default: LOOKAGAIN_HTTP_BASE_URL env var)",
    )
    p.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for reports (default: ./lookagain_results)",
    )
    p.add_argument(
        "--format",
        type=str,
        default=None,
        help="Report formats: terminal,json,markdown (comma-separated)",
    )
    p.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Path to custom test_cases directory (default: built-in)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Estimate token usage without running tests",
    )
    p.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key for the selected provider (default: provider-specific env var)",
    )
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file (default: .lookagain.yaml)",
    )


def _estimate_tokens(test_case_count: int) -> None:
    """Print estimated token usage."""
    # Conservative estimates per test case
    # Each test case ≈ 1 model call + optional judge call + optional embedding call
    model_calls = test_case_count * 1.5  # avg calls per test case
    judge_calls = test_case_count * 0.4  # ~40% of cases need judge
    embed_calls = test_case_count * 1.2  # embedding calls for wrong/corruption

    est_model_tokens = model_calls * 800  # ~800 tokens per call (input+output)
    est_judge_tokens = judge_calls * 600
    est_embed_tokens = embed_calls * 200

    total_tokens = est_model_tokens + est_judge_tokens + est_embed_tokens

    # Cost estimate at gpt-4o pricing (approx $2.50/1M input, $10/1M output)
    est_cost = total_tokens / 1_000_000 * 5.0  # blended ~$5/1M tokens

    print(f"""
Token Usage Estimate (dry-run):
  Test cases:       {test_case_count}
  Model calls:      ~{model_calls:.0f}
  Judge calls:      ~{judge_calls:.0f}
  Embedding calls:  ~{embed_calls:.0f}
  Est. total tokens: ~{total_tokens:,.0f}
  Est. cost (GPT-4o): ~${est_cost:.2f}
""")


def _count_test_cases(data_dir: str) -> int:
    """Count total test cases across all scenario files.

    Args:
        data_dir: Path to the test_cases directory.

    Returns:
        Total number of test cases.
    """
    import json

    count = 0
    for filename in [
        "missing_image.json",
        "wrong_image.json",
        "corruption.json",
        "text_bias.json",
    ]:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        count += len(data)
            except (OSError, json.JSONDecodeError):
                pass
    return count


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if args.command != "audit":
        parser.print_help()
        return

    # Setup logging
    setup_logging()

    # Load configuration
    from lookagain.config import get_default_config_path, load_config

    config_file = args.config or get_default_config_path()
    cli_args = {
        "provider": args.provider,
        "model": args.model,
        "api_key": args.api_key,
        "base_url": args.base_url,
        "judge_provider": args.judge_provider,
        "judge": args.judge,
        "output": args.output,
        "format": args.format,
        "data_dir": args.data_dir,
    }
    config = load_config(config_file=config_file, cli_args=cli_args)

    # Resolve data directory
    if config.data_dir:
        data_dir = config.data_dir
    else:
        # Default: look for data/test_cases relative to package
        package_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(package_dir, "..", "..", "data", "test_cases")
        data_dir = os.path.normpath(data_dir)

    # Dry-run mode
    if args.dry_run:
        test_case_count = _count_test_cases(data_dir)
        _estimate_tokens(test_case_count)
        return

    if not os.path.isdir(data_dir):
        logger.error(f"Test cases directory not found: {data_dir}")
        logger.info("Use --data-dir to specify a custom path.")
        sys.exit(1)

    # Lazy imports (so --help is fast)
    from lookagain.judge.factory import create_judge
    from lookagain.models.factory import create_model
    from lookagain.test_suite import run_audit

    # Build model adapter
    model_kwargs = {"model_name": config.model.model}
    if config.model.provider == "http":
        model_kwargs["base_url"] = config.model.base_url
    if config.model.api_key:
        model_kwargs["api_key"] = config.model.api_key

    model = create_model(config.model.provider, **model_kwargs)

    # Build judge adapter
    judge_provider = config.judge.provider or config.model.provider
    judge_model_name = config.judge.model or config.model.model
    judge_kwargs = {"model_name": judge_model_name}
    if config.judge.api_key:
        judge_kwargs["api_key"] = config.judge.api_key
    if judge_provider == "http":
        judge_kwargs["base_url"] = config.model.base_url

    judge = create_judge(judge_provider, **judge_kwargs)

    # Parse formats
    formats = config.output.formats

    logger.info("LookAgain")
    logger.info(f"  Provider:         {config.model.provider}")
    logger.info(f"  Model under test: {config.model.model}")
    logger.info(f"  Judge provider:   {judge_provider}")
    logger.info(f"  Judge:            {judge_model_name}")
    logger.info(f"  Output:           {config.output.directory}")
    logger.info(f"  Formats:          {formats}")

    # Run audit
    score_data = run_audit(
        model=model,
        judge=judge,
        data_dir=data_dir,
        output_dir=config.output.directory,
        formats=formats,
    )

    logger.info(f"\nAudit complete. LookAgain Score: {score_data['mirage_score']}/100")


if __name__ == "__main__":
    main()
