"""Tests for Config class."""

import logging
from pathlib import Path

from internacia.config import Config


class TestConfigGetDbPath:
    """Test get_db_path method."""

    def test_get_db_path_explicit(self):
        """Test with explicit path."""
        explicit_path = Path("/explicit/path/db.duckdb")
        result = Config.get_db_path(explicit_path=explicit_path)
        assert result == explicit_path

    def test_get_db_path_env_var(self, monkeypatch):
        """Test with environment variable."""
        env_path = "/env/path/db.duckdb"
        monkeypatch.setenv("INTERNACIA_DB_PATH", env_path)
        result = Config.get_db_path()
        assert result == Path(env_path)

    def test_get_db_path_uses_newest_cached_release(self, tmp_path, monkeypatch):
        """Without an explicit path, the newest cached release is used (no sibling probe)."""
        monkeypatch.delenv("INTERNACIA_DB_PATH", raising=False)
        monkeypatch.delenv("INTERNACIA_DATA_VERSION", raising=False)
        monkeypatch.setenv("INTERNACIA_CACHE_DIR", str(tmp_path))
        for tag in ("v3.0.0", "v3.1.0"):
            (tmp_path / tag).mkdir()
            (tmp_path / tag / "internacia.duckdb").write_bytes(b"x")
        assert Config.get_db_path() == tmp_path / "v3.1.0" / "internacia.duckdb"

    def test_get_db_path_pinned_version(self, tmp_path, monkeypatch):
        """A pinned data version selects that cached release, or nothing if it is missing."""
        monkeypatch.delenv("INTERNACIA_DB_PATH", raising=False)
        monkeypatch.setenv("INTERNACIA_CACHE_DIR", str(tmp_path))
        for tag in ("v3.0.0", "v3.1.0"):
            (tmp_path / tag).mkdir()
            (tmp_path / tag / "internacia.duckdb").write_bytes(b"x")
        assert Config.get_db_path(data_version="3.0.0") == tmp_path / "v3.0.0" / "internacia.duckdb"
        monkeypatch.setenv("INTERNACIA_DATA_VERSION", "v3.1.0")
        assert Config.get_db_path() == tmp_path / "v3.1.0" / "internacia.duckdb"
        assert Config.get_db_path(data_version="3.9.0") is None

    def test_get_db_path_not_found(self, tmp_path, monkeypatch):
        """Test when no path is found."""
        monkeypatch.delenv("INTERNACIA_DB_PATH", raising=False)
        monkeypatch.delenv("INTERNACIA_DATA_VERSION", raising=False)
        monkeypatch.setenv("INTERNACIA_CACHE_DIR", str(tmp_path))
        assert Config.get_db_path() is None


class TestConfigGetLogLevel:
    """Test get_log_level method."""

    def test_get_log_level_default(self, monkeypatch):
        """Test default log level."""
        monkeypatch.delenv("INTERNACIA_LOG_LEVEL", raising=False)
        result = Config.get_log_level()
        assert result == logging.WARNING

    def test_get_log_level_debug(self, monkeypatch):
        """Test DEBUG log level."""
        monkeypatch.setenv("INTERNACIA_LOG_LEVEL", "DEBUG")
        result = Config.get_log_level()
        assert result == logging.DEBUG

    def test_get_log_level_info(self, monkeypatch):
        """Test INFO log level."""
        monkeypatch.setenv("INTERNACIA_LOG_LEVEL", "INFO")
        result = Config.get_log_level()
        assert result == logging.INFO

    def test_get_log_level_warning(self, monkeypatch):
        """Test WARNING log level."""
        monkeypatch.setenv("INTERNACIA_LOG_LEVEL", "WARNING")
        result = Config.get_log_level()
        assert result == logging.WARNING

    def test_get_log_level_error(self, monkeypatch):
        """Test ERROR log level."""
        monkeypatch.setenv("INTERNACIA_LOG_LEVEL", "ERROR")
        result = Config.get_log_level()
        assert result == logging.ERROR

    def test_get_log_level_critical(self, monkeypatch):
        """Test CRITICAL log level."""
        monkeypatch.setenv("INTERNACIA_LOG_LEVEL", "CRITICAL")
        result = Config.get_log_level()
        assert result == logging.CRITICAL

    def test_get_log_level_invalid(self, monkeypatch):
        """Test invalid log level falls back to default."""
        monkeypatch.setenv("INTERNACIA_LOG_LEVEL", "INVALID")
        result = Config.get_log_level()
        assert result == logging.WARNING

    def test_get_log_level_case_insensitive(self, monkeypatch):
        """Test that log level is case insensitive."""
        monkeypatch.setenv("INTERNACIA_LOG_LEVEL", "debug")
        result = Config.get_log_level()
        assert result == logging.DEBUG


class TestConfigSetupLogging:
    """Test setup_logging method."""

    def test_setup_logging_adds_no_handlers(self, monkeypatch):
        """A library must leave handlers to the application."""
        monkeypatch.delenv("INTERNACIA_LOG_LEVEL", raising=False)
        logger = Config.setup_logging("test_logger")
        assert logger.handlers == []
        assert logger.level == logging.NOTSET

    def test_setup_logging_sets_level_from_env(self, monkeypatch):
        """INTERNACIA_LOG_LEVEL sets the SDK logger level."""
        monkeypatch.setenv("INTERNACIA_LOG_LEVEL", "DEBUG")
        logger = Config.setup_logging("test_logger_3")
        assert logger.level == logging.DEBUG
        assert logger.handlers == []

    def test_package_logger_has_null_handler(self):
        import internacia  # noqa: F401

        handlers = logging.getLogger("internacia").handlers
        assert any(isinstance(h, logging.NullHandler) for h in handlers)
