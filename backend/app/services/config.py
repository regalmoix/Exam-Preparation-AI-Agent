from __future__ import annotations

import logging
import os
import platform
import secrets

from dotenv import find_dotenv
from dotenv import load_dotenv
from dotenv import set_key
from openai import OpenAI


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
        
        # Check if vector store needs to be created
        self._create_vector_store_if_needed(dotenv_path)
        
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

    def _create_vector_store_if_needed(self, dotenv_path: str | None) -> None:
        """Create vector store if EXAM_PREP_VECTOR_STORE_ID is set to placeholder value."""
        placeholder_value = "vs_your-vector-store-id-here"
        current_value = os.getenv("EXAM_PREP_VECTOR_STORE_ID")
        
        if current_value != placeholder_value:
            return
        
        logger.info("Detected placeholder vector store ID, creating new vector store...")
        
        if not dotenv_path:
            raise RuntimeError(
                "Cannot create vector store: .env file not found. "
                "Please create a .env file first."
            )
        
        # Generate vector store name
        try:
            hostname = platform.node() or ""
            if not hostname:
                try:
                    import socket
                    hostname = socket.gethostname() or ""
                except Exception:
                    pass
            
            if hostname:
                identifier = hostname
            else:
                identifier = secrets.token_hex(4)
            
            store_name = f"Hackathon - {identifier}"
        except Exception as e:
            logger.warning(f"Failed to get hostname, using random identifier: {e}")
            identifier = secrets.token_hex(4)
            store_name = f"Hackathon - {identifier}"
        
        # Create vector store via OpenAI API
        try:
            client = OpenAI(api_key=self.openai_api_key)
            logger.debug(f"Creating vector store with name: {store_name}")
            vector_store = client.vector_stores.create(name=store_name)
            new_vector_store_id = vector_store.id
            logger.info(f"Successfully created vector store: {new_vector_store_id}")
        except Exception as e:
            error_msg = f"Failed to create vector store: {e!s}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        
        # Update .env file
        try:
            set_key(dotenv_path, "EXAM_PREP_VECTOR_STORE_ID", new_vector_store_id)
            logger.info(f"Updated .env file with new vector store ID: {new_vector_store_id}")
            # Reload environment to pick up the new value
            load_dotenv(dotenv_path, override=True)
        except Exception as e:
            error_msg = f"Failed to update .env file: {e!s}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

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
