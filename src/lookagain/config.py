"""Configuration management for LookAgain.

Supports loading configuration from:
1. Configuration file (YAML/TOML)
2. Environment variables
3. CLI arguments (highest priority)
"""

import os
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ModelConfig:
    """Model configuration."""
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None


@dataclass
class JudgeConfig:
    """Judge configuration."""
    provider: Optional[str] = None  # Defaults to model provider
    model: Optional[str] = None  # Defaults to model name
    api_key: Optional[str] = None


@dataclass
class EmbeddingConfig:
    """Embedding configuration."""
    provider: str = "openai"
    model: str = "text-embedding-3-small"
    api_key: Optional[str] = None


@dataclass
class ScenarioConfig:
    """Scenario thresholds configuration."""
    similarity_threshold: float = 0.70
    corruption_auc_threshold: float = 0.85


@dataclass
class OutputConfig:
    """Output configuration."""
    directory: str = "./lookagain_results"
    formats: list[str] = field(default_factory=lambda: ["terminal", "json", "markdown"])


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: Optional[str] = None


@dataclass
class LookAgainConfig:
    """Main configuration class."""
    model: ModelConfig = field(default_factory=ModelConfig)
    judge: JudgeConfig = field(default_factory=JudgeConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    scenario: ScenarioConfig = field(default_factory=ScenarioConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    data_dir: Optional[str] = None


def load_config_from_env(config: LookAgainConfig) -> LookAgainConfig:
    """Load configuration from environment variables.

    Environment variables:
        LOOKAGAIN_PROVIDER: Model provider
        LOOKAGAIN_MODEL: Model name
        LOOKAGAIN_API_KEY: API key
        LOOKAGAIN_HTTP_BASE_URL: Base URL for HTTP provider
        LOOKAGAIN_JUDGE_PROVIDER: Judge provider
        LOOKAGAIN_JUDGE_MODEL: Judge model
        LOOKAGAIN_OUTPUT_DIR: Output directory
        LOOKAGAIN_LOG_LEVEL: Logging level
        LOOKAGAIN_DATA_DIR: Test cases directory
    """
    if provider := os.environ.get("LOOKAGAIN_PROVIDER"):
        config.model.provider = provider

    if model := os.environ.get("LOOKAGAIN_MODEL"):
        config.model.model = model

    if api_key := os.environ.get("LOOKAGAIN_API_KEY"):
        config.model.api_key = api_key
        config.judge.api_key = api_key
        config.embedding.api_key = api_key

    if base_url := os.environ.get("LOOKAGAIN_HTTP_BASE_URL"):
        config.model.base_url = base_url

    if judge_provider := os.environ.get("LOOKAGAIN_JUDGE_PROVIDER"):
        config.judge.provider = judge_provider

    if judge_model := os.environ.get("LOOKAGAIN_JUDGE_MODEL"):
        config.judge.model = judge_model

    if output_dir := os.environ.get("LOOKAGAIN_OUTPUT_DIR"):
        config.output.directory = output_dir

    if log_level := os.environ.get("LOOKAGAIN_LOG_LEVEL"):
        config.logging.level = log_level

    if data_dir := os.environ.get("LOOKAGAIN_DATA_DIR"):
        config.data_dir = data_dir

    return config


def load_config_from_file(file_path: str) -> Optional[dict[str, Any]]:
    """Load configuration from a file (JSON, YAML, or TOML).

    Args:
        file_path: Path to configuration file.

    Returns:
        Configuration dictionary or None if file not found.
    """
    if not os.path.exists(file_path):
        return None

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".json":
        import json
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    elif ext in (".yaml", ".yml"):
        try:
            import yaml
            with open(file_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except ImportError as err:
            raise ImportError("PyYAML is required for YAML configuration files") from err

    elif ext == ".toml":
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError as err:
                raise ImportError("tomli is required for TOML configuration files on Python < 3.11") from err
        with open(file_path, "rb") as f:
            return tomllib.load(f)

    else:
        raise ValueError(f"Unsupported configuration file format: {ext}")


def load_config(
    config_file: Optional[str] = None,
    cli_args: Optional[dict[str, Any]] = None,
) -> LookAgainConfig:
    """Load configuration from multiple sources with priority.

    Priority (highest to lowest):
        1. CLI arguments
        2. Environment variables
        3. Configuration file
        4. Defaults

    Args:
        config_file: Path to configuration file.
        cli_args: Dictionary of CLI arguments.

    Returns:
        LookAgainConfig instance.
    """
    config = LookAgainConfig()

    # Load from file (lowest priority)
    if config_file:
        file_config = load_config_from_file(config_file)
        if file_config:
            # Apply file config to dataclasses
            if "model" in file_config:
                for k, v in file_config["model"].items():
                    if hasattr(config.model, k):
                        setattr(config.model, k, v)

            if "judge" in file_config:
                for k, v in file_config["judge"].items():
                    if hasattr(config.judge, k):
                        setattr(config.judge, k, v)

            if "embedding" in file_config:
                for k, v in file_config["embedding"].items():
                    if hasattr(config.embedding, k):
                        setattr(config.embedding, k, v)

            if "scenario" in file_config:
                for k, v in file_config["scenario"].items():
                    if hasattr(config.scenario, k):
                        setattr(config.scenario, k, v)

            if "output" in file_config:
                for k, v in file_config["output"].items():
                    if hasattr(config.output, k):
                        setattr(config.output, k, v)

            if "logging" in file_config:
                for k, v in file_config["logging"].items():
                    if hasattr(config.logging, k):
                        setattr(config.logging, k, v)

            if "data_dir" in file_config:
                config.data_dir = file_config["data_dir"]

    # Load from environment variables (medium priority)
    config = load_config_from_env(config)

    # Apply CLI arguments (highest priority)
    if cli_args:
        if provider := cli_args.get("provider"):
            config.model.provider = provider
        if model := cli_args.get("model"):
            config.model.model = model
        if api_key := cli_args.get("api_key"):
            config.model.api_key = api_key
            config.judge.api_key = api_key
            config.embedding.api_key = api_key
        if base_url := cli_args.get("base_url"):
            config.model.base_url = base_url
        if judge_provider := cli_args.get("judge_provider"):
            config.judge.provider = judge_provider
        if judge_model := cli_args.get("judge"):
            config.judge.model = judge_model
        if output := cli_args.get("output"):
            config.output.directory = output
        if formats := cli_args.get("format"):
            config.output.formats = [f.strip() for f in formats.split(",")]
        if data_dir := cli_args.get("data_dir"):
            config.data_dir = data_dir

    return config


def get_default_config_path() -> str:
    """Get the default configuration file path.

    Returns:
        Path to default config file (.lookagain.yaml in current directory).
    """
    return os.path.join(os.getcwd(), ".lookagain.yaml")
