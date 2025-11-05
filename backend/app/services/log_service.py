from __future__ import annotations

import logging
import sys


class LogColors:
    """ANSI color codes for colorized logging output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Log level colors
    DEBUG = "\033[36m"  # Cyan/Blue
    INFO = "\033[32m"  # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"  # Red
    CRITICAL = "\033[35m"  # Magenta

    # Component colors
    TIMESTAMP = "\033[90m"  # Dark gray
    NAME = "\033[94m"  # Light blue


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log output."""

    def __init__(self):
        super().__init__()

        # Define format for each log level
        self.formats = {
            logging.DEBUG: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.DEBUG}%(levelname)s{LogColors.RESET} - %(message)s",
            logging.INFO: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.INFO}%(levelname)s{LogColors.RESET} - %(message)s",
            logging.WARNING: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.WARNING}%(levelname)s{LogColors.RESET} - %(message)s",
            logging.ERROR: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.ERROR}%(levelname)s{LogColors.RESET} - %(message)s",
            logging.CRITICAL: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.CRITICAL}%(levelname)s{LogColors.RESET} - %(message)s",
        }

        # Default format (fallback)
        self.default_format = f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - %(levelname)s - %(message)s"

    def format(self, record):
        # Get the format for this log level
        log_format = self.formats.get(record.levelno, self.default_format)

        # Create formatter with the appropriate format
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

        return formatter.format(record)


def setup_logging():
    """Set up logging configuration for the application."""
    import os

    # Check both LOG_LEVEL and DEBUG environment variables
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    debug_mode = os.getenv("DEBUG") not in (None, "0", "false", 0, False, "False")

    # If DEBUG is enabled, override log level to DEBUG
    if debug_mode:
        log_level = "DEBUG"

    # Check if we're running in a terminal that supports colors
    supports_color = (
        # Force color if explicitly requested
        os.getenv("FORCE_COLOR") is not None
        or
        # Or if running in a proper terminal
        (hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and os.getenv("TERM") != "dumb")
    ) and os.getenv("NO_COLOR") is None  # But respect NO_COLOR override

    # Create console handler with colored formatter
    console_handler = logging.StreamHandler(sys.stdout)

    if supports_color:
        console_handler.setFormatter(ColoredFormatter())
    else:
        # Fallback to plain formatter
        plain_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(plain_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Remove existing handlers to avoid duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add our custom handler
    root_logger.addHandler(console_handler)

    # Set specific loggers to appropriate levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Reduce noise from external libraries unless in debug mode
    if debug_mode:
        logging.getLogger("urllib3").setLevel(logging.DEBUG)
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("openai").setLevel(logging.DEBUG)
    else:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.INFO)

    color_status = "enabled" if supports_color else "disabled"
    print(f"[STARTUP] Logging configured: level={log_level}, debug_mode={debug_mode}, colors={color_status}")


setup_logging()
