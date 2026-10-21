"""Tests for the release downloader and cache (network mocked)."""

import hashlib
import logging
from unittest.mock import Mock, patch

import pytest
import requests

from internacia import downloader
from internacia.exceptions import DownloadError, VersionError

DB_BYTES = b"duckdb file bytes"
DB_SHA = hashlib.sha256(DB_BYTES).hexdigest()


@pytest.fixture(autouse=True)
def cache(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("INTERNACIA_CACHE_DIR", str(cache_dir))
    monkeypatch.delenv("INTERNACIA_DATA_VERSION", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    return cache_dir


def _cached(cache_dir, *tags):
    for tag in tags:
        (cache_dir / tag).mkdir(parents=True, exist_ok=True)
        (cache_dir / tag / "internacia.duckdb").write_bytes(b"x")


def _redirect(tag):
    response = Mock(status_code=302, headers={"Location": f"{downloader.RELEASES_URL}/tag/{tag}"})
    return response


def _fake_get(checksums: str | None, db_bytes: bytes = DB_BYTES):
    """requests.get stand-in serving the database file and SHA256SUMS."""
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        response = Mock()
        response.raise_for_status = Mock()
        if url.endswith("/SHA256SUMS"):
            response.status_code = 404 if checksums is None else 200
            response.text = checksums or ""
        else:
            response.status_code = 200
            response.headers = {"content-length": str(len(db_bytes))}
            response.iter_content = Mock(return_value=[db_bytes])
        return response

    get.calls = calls
    return get


class TestVersions:
    @pytest.mark.parametrize(
        ("value", "expected"), [("v3.1.0", (3, 1, 0)), ("3.10.2", (3, 10, 2)), ("latest", None)]
    )
    def test_parse_version(self, value, expected):
        assert downloader.parse_version(value) == expected

    def test_release_tag_normalizes_and_rejects(self):
        assert downloader.release_tag("3.1.0") == "v3.1.0"
        with pytest.raises(VersionError):
            downloader.release_tag("latest")


class TestCache:
    def test_cache_dir_from_env_is_created(self, cache):
        assert downloader.get_cache_dir() == cache
        assert cache.is_dir()

    def test_cache_dir_default(self, tmp_path, monkeypatch):
        monkeypatch.delenv("INTERNACIA_CACHE_DIR")
        with patch("internacia.downloader.Path.home", return_value=tmp_path):
            assert downloader.get_cache_dir() == tmp_path / ".internacia"

    def test_cached_versions_sorted_by_semver(self, cache):
        _cached(cache, "v3.9.0", "v3.10.0", "v2.2.0")
        (cache / "v3.11.0").mkdir()  # no database inside
        (cache / "notes").mkdir()
        assert downloader.cached_versions() == ["v3.10.0", "v3.9.0", "v2.2.0"]

    def test_cached_path_prefers_newest_supported_major(self, cache):
        _cached(cache, "v3.1.0", "v3.2.0", "v4.0.0")
        assert downloader.get_cached_database_path() == cache / "v3.2.0" / "internacia.duckdb"

    def test_cached_path_for_version_and_legacy_fallback(self, cache):
        assert (
            downloader.get_cached_database_path("3.0.0") == cache / "v3.0.0" / "internacia.duckdb"
        )
        assert downloader.get_cached_database_path() == cache / "internacia.duckdb"


class TestLatestVersion:
    def test_latest_from_redirect_without_api(self):
        with (
            patch("internacia.downloader.requests.head", return_value=_redirect("v3.2.0")) as head,
            patch("internacia.downloader.requests.get") as get,
        ):
            assert downloader.get_latest_version() == "v3.2.0"
        head.assert_called_once()
        get.assert_not_called()

    def test_newer_major_falls_back_to_newest_supported_release(self):
        releases = [
            {"tag_name": "v4.0.0", "assets": [{"name": "internacia.duckdb"}]},
            {"tag_name": "v3.3.0", "assets": [{"name": "internacia.duckdb"}]},
            {"tag_name": "v3.4.0", "assets": [{"name": "README.md"}]},
        ]
        api = Mock(status_code=200, json=Mock(return_value=releases), raise_for_status=Mock())
        with (
            patch("internacia.downloader.requests.head", return_value=_redirect("v4.0.0")),
            patch("internacia.downloader.requests.get", return_value=api),
        ):
            assert downloader.get_latest_version() == "v3.3.0"

    def test_no_supported_release(self):
        api = Mock(status_code=200, json=Mock(return_value=[]), raise_for_status=Mock())
        with (
            patch("internacia.downloader.requests.head", return_value=_redirect("v4.0.0")),
            patch("internacia.downloader.requests.get", return_value=api),
        ):
            with pytest.raises(VersionError):
                downloader.get_latest_version()

    def test_unresolvable_latest(self):
        with patch(
            "internacia.downloader.requests.head", return_value=Mock(status_code=404, headers={})
        ):
            with pytest.raises(DownloadError):
                downloader.get_latest_version()
        with patch(
            "internacia.downloader.requests.head",
            side_effect=requests.exceptions.ConnectionError("down"),
        ):
            with pytest.raises(DownloadError):
                downloader.get_latest_version()


class TestListReleases:
    def test_uses_github_token(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "secret")
        api = Mock(
            status_code=200,
            raise_for_status=Mock(),
            json=Mock(
                return_value=[{"tag_name": "v3.0.0", "assets": [{"name": "internacia.duckdb"}]}]
            ),
        )
        with patch("internacia.downloader.requests.get", return_value=api) as get:
            releases = downloader.list_releases()
        assert get.call_args.kwargs["headers"]["Authorization"] == "Bearer secret"
        assert releases[0]["has_database"] and not releases[0]["has_checksums"]

    def test_error(self):
        with patch(
            "internacia.downloader.requests.get",
            side_effect=requests.exceptions.ConnectionError("x"),
        ):
            with pytest.raises(DownloadError):
                downloader.list_releases()


class TestDownload:
    def test_download_verifies_checksum(self, cache):
        get = _fake_get(f"{DB_SHA}  internacia.duckdb\nabc  other.json\n")
        with patch("internacia.downloader.requests.get", side_effect=get):
            path = downloader.download_database("3.1.0", show_progress=False)
        assert path == cache / "v3.1.0" / "internacia.duckdb"
        assert path.read_bytes() == DB_BYTES
        assert get.calls[0] == downloader.DOWNLOAD_URL.format(
            tag="v3.1.0", name="internacia.duckdb"
        )

    def test_checksum_mismatch_leaves_no_file(self, cache):
        get = _fake_get("0" * 64 + "  internacia.duckdb\n")
        with patch("internacia.downloader.requests.get", side_effect=get):
            with pytest.raises(DownloadError, match="failed verification"):
                downloader.download_database("v3.1.0", show_progress=False)
        assert not list((cache / "v3.1.0").iterdir())

    def test_release_without_checksums_warns(self, cache, caplog):
        with patch("internacia.downloader.requests.get", side_effect=_fake_get(None)):
            with caplog.at_level(logging.WARNING, logger="internacia.downloader"):
                path = downloader.download_database("v3.0.0", show_progress=False)
        assert path.read_bytes() == DB_BYTES
        assert "no SHA256SUMS" in caplog.text

    def test_cached_release_is_not_downloaded_again(self, cache):
        _cached(cache, "v3.0.0")
        with patch("internacia.downloader.requests.get") as get:
            assert downloader.download_database("v3.0.0") == cache / "v3.0.0" / "internacia.duckdb"
        get.assert_not_called()

    def test_force_redownloads(self, cache):
        _cached(cache, "v3.0.0")
        with patch(
            "internacia.downloader.requests.get",
            side_effect=_fake_get(f"{DB_SHA}  internacia.duckdb\n"),
        ):
            path = downloader.download_database("v3.0.0", force=True, show_progress=False)
        assert path.read_bytes() == DB_BYTES

    def test_default_is_pinned_version_then_latest(self, cache, monkeypatch):
        get = _fake_get(None)
        monkeypatch.setenv("INTERNACIA_DATA_VERSION", "3.0.0")
        with (
            patch("internacia.downloader.requests.get", side_effect=get),
            patch("internacia.downloader.requests.head") as head,
        ):
            assert downloader.download_database(show_progress=False).parent.name == "v3.0.0"
        head.assert_not_called()
        monkeypatch.delenv("INTERNACIA_DATA_VERSION")
        with (
            patch("internacia.downloader.requests.get", side_effect=get),
            patch("internacia.downloader.requests.head", return_value=_redirect("v3.2.0")),
        ):
            assert downloader.download_database(show_progress=False).parent.name == "v3.2.0"

    def test_missing_release_file(self, cache):
        response = Mock(status_code=404, raise_for_status=Mock())
        with patch("internacia.downloader.requests.get", return_value=response):
            with pytest.raises(DownloadError, match="Not found"):
                downloader.download_database("v9.9.9", show_progress=False)

    def test_network_error(self, cache):
        with patch(
            "internacia.downloader.requests.get",
            side_effect=requests.exceptions.ConnectionError("x"),
        ):
            with pytest.raises(DownloadError):
                downloader.download_database("v3.0.0", show_progress=False)


class TestCheckForUpdates:
    @pytest.mark.parametrize(
        ("cached", "has_update", "current"),
        [((), True, None), (("v3.0.0",), True, "v3.0.0"), (("v3.0.0", "v3.2.0"), False, "v3.2.0")],
    )
    def test_compares_semver(self, cache, cached, has_update, current):
        _cached(cache, *cached)
        with patch("internacia.downloader.requests.head", return_value=_redirect("v3.2.0")):
            result = downloader.check_for_updates()
        assert result["has_update"] is has_update
        assert result["current_version"] == current
        assert result["latest_version"] == "v3.2.0"
        assert (result["current_path"] is None) is (current is None)
