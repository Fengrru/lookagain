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
        default="openai",
        help=f"VLM provider (default: openai). Supported: {providers}",
    )
    p.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
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
        help="Base URL for HTTP/local provider (default: MIRAGE_HTTP_BASE_URL env var)",
    )
    p.add_argument(
        "--output",
        type=str,
        default="./mirage_results",
        help="Output directory for reports (default: ./mirage_results)",
    )
    p.add_argument(
        "--format",
        type=str,
        default="terminal,json,markdown",
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


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if args.command != "audit":
        parser.print_help()
        return

    # Dry-run mode
    if args.dry_run:
        _estimate_tokens(test_case_count=50)
        return

    # Lazy imports (so --help is fast)
    from lookagain.judge.factory import create_judge
    from lookagain.models.factory import create_model
    from lookagain.test_suite import run_audit

    # Resolve data directory
    if args.data_dir:
        data_dir = args.data_dir
    else:
        # Default: look for data/test_cases relative to package
        package_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(package_dir, "..", "..", "data", "test_cases")
        data_dir = os.path.normpath(data_dir)

    if not os.path.isdir(data_dir):
        print(f"Error: test_cases directory not found: {data_dir}")
        print("Use --data-dir to specify a custom path.")
        sys.exit(1)

    # Build model adapter
    model_kwargs = {"model_name": args.model}
    if args.provider == "http":
        model_kwargs["base_url"] = args.base_url
    if args.api_key:
        model_kwargs["api_key"] = args.api_key

    model = create_model(args.provider, **model_kwargs)

    # Build judge adapter
    judge_provider = args.judge_provider or args.provider
    judge_model_name = args.judge or args.model
    judge_kwargs = {"model_name": judge_model_name}
    if args.api_key:
        judge_kwargs["api_key"] = args.api_key
    if judge_provider == "http":
        judge_kwargs["base_url"] = args.base_url

    judge = create_judge(judge_provider, **judge_kwargs)

    # Parse formats
    formats = [f.strip() for f in args.format.split(",")]

    print("LookAgain")
    print(f"  Provider:         {args.provider}")
    print(f"  Model under test: {args.model}")
    print(f"  Judge provider:   {judge_provider}")
    print(f"  Judge:            {judge_model_name}")
    print(f"  Output:           {args.output}")
    print(f"  Formats:          {formats}")
    print()

    # Run audit
    score_data = run_audit(
        model=model,
        judge=judge,
        data_dir=data_dir,
        output_dir=args.output,
        formats=formats,
    )

    print(f"\nAudit complete. Mirage Score: {score_data['mirage_score']}/100")


if __name__ == "__main__":
    main()
