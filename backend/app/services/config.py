from __future__ import annotations

import logging
import os

from dotenv import find_dotenv
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        dotenv_path = find_dotenv()
        if dotenv_path:
            logger.debug(f"Loading environment from {dotenv_path}")
            load_dotenv(dotenv_path)
        else:
            logger.warning("No .env file found")

        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
        self.notion_token = self._get_required_env("NOTION_TOKEN")
        self.exam_prep_vector_store_id = self._get_required_env("EXAM_PREP_VECTOR_STORE_ID")

        self.logfire_token = os.getenv("LOGFIRE_TOKEN", "")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    @staticmethod
    def _get_required_env(key: str) -> str:
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
            self._get_required_env("NOTION_TOKEN")
            logger.info("Configuration validation successful")
            return True
        except RuntimeError:
            logger.error("Configuration validation failed")
            return False


config = Config()
