"""
Utility functions and helpers for the RAG system.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
import sys


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
):
    """
    Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        log_format: Optional custom log format
    """
    # Remove default handler
    logger.remove()

    # Default format
    if log_format is None:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

    # Add console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True
    )

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format=log_format,
            level=log_level,
            rotation="10 MB",
            retention="1 week",
            compression="zip"
        )

    logger.info(f"Logging initialized at {log_level} level")


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)

    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded configuration from {config_path}")
    return config


def save_config(config: Dict[str, Any], config_path: str):
    """
    Save configuration to YAML file.

    Args:
        config: Configuration dictionary
        config_path: Path to save config
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    logger.info(f"Saved configuration to {config_path}")


def load_env_file(env_path: str = ".env"):
    """
    Load environment variables from .env file.

    Args:
        env_path: Path to .env file
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")
    except ImportError:
        logger.warning("python-dotenv not installed, skipping .env loading")
    except Exception as e:
        logger.warning(f"Could not load .env file: {e}")


def ensure_directory(directory: str):
    """
    Ensure directory exists, create if not.

    Args:
        directory: Directory path
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {directory}")


def get_file_size(file_path: str) -> str:
    """
    Get human-readable file size.

    Args:
        file_path: Path to file

    Returns:
        Formatted file size string
    """
    size_bytes = Path(file_path).stat().st_size

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.2f} TB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"


def validate_file_exists(file_path: str, file_type: str = "file") -> bool:
    """
    Validate that a file exists.

    Args:
        file_path: Path to file
        file_type: Type description for error message

    Returns:
        True if exists, raises exception otherwise
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"{file_type} not found: {file_path}")

    return True


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries.
    Later configs override earlier ones.

    Args:
        *configs: Configuration dictionaries to merge

    Returns:
        Merged configuration
    """
    merged = {}

    for config in configs:
        if config:
            merged.update(config)

    return merged


def create_gitkeep_files(directories: list):
    """
    Create .gitkeep files in empty directories.

    Args:
        directories: List of directory paths
    """
    for directory in directories:
        ensure_directory(directory)
        gitkeep_path = Path(directory) / ".gitkeep"

        if not gitkeep_path.exists():
            gitkeep_path.touch()
            logger.debug(f"Created .gitkeep in {directory}")


class ProgressTracker:
    """
    Simple progress tracker for batch operations.
    """

    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items
            description: Description of operation
        """
        self.total = total
        self.current = 0
        self.description = description

    def update(self, n: int = 1):
        """
        Update progress.

        Args:
            n: Number of items processed
        """
        self.current += n
        percentage = (self.current / self.total) * 100

        logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")

    def finish(self):
        """Mark operation as finished."""
        logger.info(f"{self.description}: Complete! ({self.total} items)")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re

    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')

    return sanitized


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def parse_power_unit(power_str: str) -> tuple[float, str]:
    """
    Parse power value with unit.

    Args:
        power_str: Power string (e.g., "100 MW", "50 kW")

    Returns:
        Tuple of (value, unit)
    """
    import re

    # Extract number and unit
    match = re.match(r'([\d.]+)\s*([A-Za-z]+)', str(power_str).strip())

    if match:
        value = float(match.group(1))
        unit = match.group(2).upper()
        return value, unit

    return 0.0, "MW"


def normalize_location(location: str) -> str:
    """
    Normalize location string.

    Args:
        location: Location string

    Returns:
        Normalized location
    """
    # Remove extra whitespace
    normalized = " ".join(location.split())

    # Capitalize first letter of each word
    normalized = normalized.title()

    return normalized


class Timer:
    """
    Context manager for timing operations.
    """

    def __init__(self, description: str = "Operation"):
        """
        Initialize timer.

        Args:
            description: Description of operation
        """
        self.description = description
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        """Start timer."""
        import time
        self.start_time = time.time()
        logger.info(f"{self.description} started...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and log duration."""
        import time
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"{self.description} completed in {format_duration(duration)}")

    @property
    def elapsed(self) -> float:
        """Get elapsed time."""
        if self.start_time is None:
            return 0.0

        import time
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time


def print_header(title: str, width: int = 80):
    """
    Print a formatted header.

    Args:
        title: Header title
        width: Total width
    """
    border = "=" * width
    padding = (width - len(title) - 2) // 2
    header = f"{border}\n{' ' * padding} {title}\n{border}"

    print(header)
    logger.info(title)


def print_table(data: list[dict], headers: Optional[list[str]] = None):
    """
    Print data as a formatted table.

    Args:
        data: List of dictionaries
        headers: Optional custom headers
    """
    if not data:
        print("No data to display")
        return

    # Get headers
    if headers is None:
        headers = list(data[0].keys())

    # Calculate column widths
    widths = {h: len(str(h)) for h in headers}
    for row in data:
        for header in headers:
            value = str(row.get(header, ""))
            widths[header] = max(widths[header], len(value))

    # Print header
    header_row = " | ".join(str(h).ljust(widths[h]) for h in headers)
    separator = "-+-".join("-" * widths[h] for h in headers)

    print(header_row)
    print(separator)

    # Print rows
    for row in data:
        row_str = " | ".join(str(row.get(h, "")).ljust(widths[h]) for h in headers)
        print(row_str)
