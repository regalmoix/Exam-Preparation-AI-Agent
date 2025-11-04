"""Configuration management for the Study Assistant AI Workshop backend."""

from __future__ import annotations

import logging
import os

from dotenv import find_dotenv
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class Config:
    """Configuration class that loads environment variables with proper defaults."""

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        logger.info("Initializing configuration")

        # Load from .env file if it exists (searches up the directory tree)
        dotenv_path = find_dotenv()
        if dotenv_path:
            logger.debug(f"Loading environment from {dotenv_path}")
            load_dotenv(dotenv_path)
        else:
            logger.warning("No .env file found")

        # Required environment variables
        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
        self.exam_prep_vector_store_id = self._get_required_env("EXAM_PREP_VECTOR_STORE_ID")

        # Optional environment variables with defaults
        self.debug = os.getenv("DEBUG") not in (None, "0", "false", 0, False, "False")
        self.api_host = os.getenv("API_HOST", "127.0.0.1")
        self.api_port = int(os.getenv("API_PORT", "8002"))

        self.frontend_port = int(os.getenv("VITE_PORT", "5172"))
        self.api_base_url = os.getenv("VITE_API_BASE_URL", f"http://{self.api_host}:{self.api_port}")

        logger.info(f"Configuration loaded - Debug: {self.debug}, API: {self.api_host}:{self.api_port}")

    @staticmethod
    def _get_required_env(key: str) -> str:
        """Get a required environment variable, raising an error if not set."""
        value = os.getenv(key)
        if not value:
            logger.error(f"Required environment variable {key} is not set")
            raise RuntimeError(
                f"{key} is not set. Please copy .env.template to .env and set this variable. "
                f"See README.md for setup instructions."
            )
        logger.debug(f"Required environment variable {key} loaded successfully")
        return value

    def validate(self) -> bool:
        logger.info("Validating configuration")
        try:
            self._get_required_env("OPENAI_API_KEY")
            self._get_required_env("EXAM_PREP_VECTOR_STORE_ID")
            logger.info("Configuration validation successful")
            return True
        except RuntimeError:
            logger.error("Configuration validation failed")
            return False


# Global configuration instance
config = Config()
