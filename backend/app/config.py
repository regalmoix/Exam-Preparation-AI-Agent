"""Configuration management for the Study Assistant AI Workshop backend."""

from __future__ import annotations

import os

from dotenv import find_dotenv
from dotenv import load_dotenv


class Config:
    """Configuration class that loads environment variables with proper defaults."""

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load from .env file if it exists (searches up the directory tree)
        load_dotenv(find_dotenv())

        # Required environment variables
        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
        self.exam_prep_vector_store_id = self._get_required_env("EXAM_PREP_VECTOR_STORE_ID")

        # Optional environment variables with defaults
        self.api_host = os.getenv("API_HOST", "127.0.0.1")
        self.api_port = int(os.getenv("API_PORT", "8002"))

        self.frontend_port = int(os.getenv("VITE_PORT", "5172"))
        self.api_base_url = os.getenv("VITE_API_BASE_URL", f"http://{self.api_host}:{self.api_port}")

    @staticmethod
    def _get_required_env(key: str) -> str:
        """Get a required environment variable, raising an error if not set."""
        value = os.getenv(key)
        if not value:
            raise RuntimeError(
                f"{key} is not set. Please copy .env.template to .env and set this variable. "
                f"See README.md for setup instructions."
            )
        return value

    def validate(self) -> bool:
        try:
            self._get_required_env("OPENAI_API_KEY")
            self._get_required_env("EXAM_PREP_VECTOR_STORE_ID")
            return True
        except RuntimeError:
            return False


# Global configuration instance
config = Config()
