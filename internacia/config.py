"""Configuration management for internacia SDK."""

import logging
import os
from pathlib import Path


class Config:
    """Configuration for internacia SDK."""

    # Environment variable names
    ENV_DB_PATH = "INTERNACIA_DB_PATH"
    ENV_LOG_LEVEL = "INTERNACIA_LOG_LEVEL"
    ENV_CACHE_DIR = "INTERNACIA_CACHE_DIR"
    ENV_DATA_VERSION = "INTERNACIA_DATA_VERSION"

    # Default values
    DEFAULT_LOG_LEVEL = logging.WARNING

    @classmethod
    def get_db_path(
        cls, explicit_path: Path | None = None, data_version: str | None = None
    ) -> Path | None:
        """
        Get the database path.

        Priority:
        1. ``explicit_path``
        2. ``INTERNACIA_DB_PATH``
        3. The cached release ``data_version`` (or ``INTERNACIA_DATA_VERSION``), if pinned
        4. The newest cached release with a supported contract major

        Returns:
            Path to the database file, or None if none is found
        """
        if explicit_path:
            return Path(explicit_path)

        env_path = os.getenv(cls.ENV_DB_PATH)
        if env_path:
            return Path(env_path)

        # Lazy import: the downloader imports Config.
        from internacia.downloader import (
            get_cached_database_path,
        )  # pylint: disable=import-outside-toplevel

        pinned = data_version or os.getenv(cls.ENV_DATA_VERSION)
        cached = get_cached_database_path(pinned)
        return cached if cached.exists() else None

    @classmethod
    def get_log_level(cls) -> int:
        """
        Get log level from environment variable or default.

        Returns:
            Logging level constant
        """
        env_level = os.getenv(cls.ENV_LOG_LEVEL, "").upper()
        if env_level:
            level_map = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL,
            }
            return level_map.get(env_level, cls.DEFAULT_LOG_LEVEL)
        return cls.DEFAULT_LOG_LEVEL

    @classmethod
    def setup_logging(cls, logger_name: str = "internacia") -> logging.Logger:
        """
        Set up logging for the SDK.

        Args:
            logger_name: Name for the logger

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(logger_name)

        # Only configure if not already configured
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(cls.get_log_level())

        return logger
