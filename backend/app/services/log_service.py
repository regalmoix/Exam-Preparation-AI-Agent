from __future__ import annotations

import logging
import sys

import logfire
from agents import enable_verbose_stdout_logging
from fastapi import FastAPI

from .config import config


class LogColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    DEBUG = "\033[36m"  # Cyan/Blue
    INFO = "\033[32m"  # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"  # Red
    CRITICAL = "\033[35m"  # Magenta

    TIMESTAMP = "\033[90m"  # Dark gray
    NAME = "\033[94m"  # Light blue


class ColoredFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

        self.formats = {
            logging.DEBUG: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.DEBUG}%(levelname)s{LogColors.RESET} - %(message)s",
            logging.INFO: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.INFO}%(levelname)s{LogColors.RESET} - %(message)s",
            logging.WARNING: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.WARNING}%(levelname)s{LogColors.RESET} - %(message)s",
            logging.ERROR: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.ERROR}%(levelname)s{LogColors.RESET} - %(message)s",
            logging.CRITICAL: f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - {LogColors.CRITICAL}%(levelname)s{LogColors.RESET} - %(message)s",
        }

        self.default_format = f"{LogColors.TIMESTAMP}%(asctime)s{LogColors.RESET} - {LogColors.NAME}%(name)s{LogColors.RESET} - %(levelname)s - %(message)s"

    def format(self, record):
        log_format = self.formats.get(record.levelno, self.default_format)
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging(app: FastAPI) -> None:
    enable_verbose_stdout_logging()
    logfire.configure(token=config.logfire_token)
    logfire.instrument_openai_agents()
    logfire.instrument_fastapi(app)

    log_level = config.log_level

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(logfire.LogfireLoggingHandler())

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.INFO)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)
