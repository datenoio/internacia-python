"""Download internacia-db release databases, verify them, and manage the local cache.

Release files are fetched from their direct GitHub download URLs, so downloading does
not use the GitHub API or its 60-requests-per-hour anonymous limit. The API is only
used to list releases (``list_releases``) or to find the newest release with a
supported contract major when the latest release has a newer one. Set ``GITHUB_TOKEN``
to authenticate those API calls.
"""

import hashlib
import logging
import os
import re
import shutil
from pathlib import Path

import requests

from internacia.config import Config
from internacia.contract import SUPPORTED_CONTRACT_MAJOR
from internacia.exceptions import DownloadError, VersionError

logger = logging.getLogger(__name__)

GITHUB_REPO = "datenoio/internacia-db"
RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases"
LATEST_RELEASE_URL = f"{RELEASES_URL}/latest"
DOWNLOAD_URL = RELEASES_URL + "/download/{tag}/{name}"
GITHUB_API_RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases"

DB_FILE = "internacia.duckdb"
CHECKSUMS_FILE = "SHA256SUMS"

_VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def parse_version(version: str) -> tuple[int, int, int] | None:
    """``"v3.1.0"`` or ``"3.1.0"`` → ``(3, 1, 0)``; None for anything else."""
    match = _VERSION_RE.match(version.strip())
    return (int(match[1]), int(match[2]), int(match[3])) if match else None


def release_tag(version: str) -> str:
    """Normalize a version to its release tag (``"3.1.0"`` → ``"v3.1.0"``)."""
    parsed = parse_version(version)
    if parsed is None:
        raise VersionError(f"Not a release version: {version!r} (expected e.g. 'v3.1.0')")
    return "v{}.{}.{}".format(*parsed)


def _api_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_cache_dir() -> Path:
    """
    Get the cache directory for downloaded databases.

    ``INTERNACIA_CACHE_DIR`` if set, else ``~/.internacia/``. Created if missing.
    """
    env_cache = os.getenv(Config.ENV_CACHE_DIR)
    cache_dir = Path(env_cache).expanduser() if env_cache else Path.home() / ".internacia"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def cached_versions() -> list[str]:
    """Release tags with a cached database, newest first (semantic version order)."""
    tags = []
    for item in get_cache_dir().iterdir():
        parsed = parse_version(item.name)
        if parsed and (item / DB_FILE).is_file():
            tags.append((parsed, item.name))
    return [name for _, name in sorted(tags, reverse=True)]


def get_cached_database_path(version: str | None = None) -> Path:
    """
    Path of a cached database.

    With ``version``: ``<cache>/<tag>/internacia.duckdb`` (which may not exist yet).
    Without: the newest cached release with a supported contract major, else the legacy
    unversioned ``<cache>/internacia.duckdb``.
    """
    cache_dir = get_cache_dir()
    if version:
        return cache_dir / release_tag(version) / DB_FILE
    for tag in cached_versions():
        parsed = parse_version(tag)
        if parsed and parsed[0] == SUPPORTED_CONTRACT_MAJOR:
            return cache_dir / tag / DB_FILE
    return cache_dir / DB_FILE


def list_releases() -> list[dict]:
    """
    List internacia-db releases via the GitHub API (uses ``GITHUB_TOKEN`` if set).

    Returns dictionaries with ``tag_name``, ``published_at``, ``has_database``,
    ``has_checksums`` and ``asset_names``, newest first.

    Raises:
        DownloadError: If the releases cannot be fetched
    """
    try:
        response = requests.get(GITHUB_API_RELEASES_URL, timeout=10, headers=_api_headers())
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise DownloadError(f"Failed to fetch releases from the GitHub API: {e}") from e
    releases = []
    for release in response.json():
        names = [asset.get("name", "") for asset in release.get("assets", [])]
        releases.append(
            {
                "tag_name": release.get("tag_name", ""),
                "published_at": release.get("published_at", ""),
                "has_database": DB_FILE in names,
                "has_checksums": CHECKSUMS_FILE in names,
                "asset_names": names,
            }
        )
    return releases


def _latest_release_tag() -> str:
    """Tag of the latest release, read from the ``/releases/latest`` redirect."""
    try:
        response = requests.head(LATEST_RELEASE_URL, allow_redirects=False, timeout=10)
    except requests.exceptions.RequestException as e:
        raise DownloadError(f"Failed to resolve the latest internacia-db release: {e}") from e
    tag = response.headers.get("Location", "").rstrip("/").rsplit("/", 1)[-1]
    if response.status_code not in (301, 302, 303, 307, 308) or parse_version(tag) is None:
        raise DownloadError(
            f"Could not resolve the latest internacia-db release from {LATEST_RELEASE_URL} "
            f"(HTTP {response.status_code})"
        )
    return tag


def get_latest_version() -> str:
    """
    Newest release tag whose contract major this SDK supports (e.g. ``"v3.1.0"``).

    Raises:
        DownloadError: If release information cannot be fetched
        VersionError: If no release has a supported contract major
    """
    tag = _latest_release_tag()
    if parse_version(tag)[0] == SUPPORTED_CONTRACT_MAJOR:  # type: ignore[index]
        return tag
    logger.info("Latest release %s has a different contract major; searching older releases", tag)
    compatible = [
        (parsed, r["tag_name"])
        for r in list_releases()
        if r["has_database"]
        and (parsed := parse_version(r["tag_name"])) is not None
        and parsed[0] == SUPPORTED_CONTRACT_MAJOR
    ]
    if not compatible:
        raise VersionError(f"No internacia-db {SUPPORTED_CONTRACT_MAJOR}.x release found")
    return str(max(compatible)[1])


def _fetch_checksums(tag: str) -> dict[str, str] | None:
    """``{file name: sha256}`` from the release's SHA256SUMS; None if the release has none."""
    url = DOWNLOAD_URL.format(tag=tag, name=CHECKSUMS_FILE)
    try:
        response = requests.get(url, timeout=30)
    except requests.exceptions.RequestException as e:
        raise DownloadError(f"Failed to download {url}: {e}") from e
    if response.status_code == 404:
        return None
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise DownloadError(f"Failed to download {url}: {e}") from e
    checksums = {}
    for line in response.text.splitlines():
        digest, _, name = line.partition("  ")
        if name:
            checksums[name.strip()] = digest.strip().lower()
    return checksums


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_file(url: str, destination: Path, show_progress: bool = True) -> None:
    """Stream ``url`` to ``destination``; a tqdm progress bar is shown when available."""
    try:
        logger.info("Downloading from: %s", url)
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 404:
            raise DownloadError(f"Not found: {url}")
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        progress = None
        if show_progress and total_size > 0:
            try:
                import tqdm  # pylint: disable=import-outside-toplevel

                progress = tqdm.tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc="Downloading",
                )
            except ImportError:
                progress = None
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=1 << 16):
                if chunk:
                    f.write(chunk)
                    if progress is not None:
                        progress.update(len(chunk))
        if progress is not None:
            progress.close()
    except requests.exceptions.RequestException as e:
        destination.unlink(missing_ok=True)
        raise DownloadError(f"Download failed: {e}") from e
    except OSError as e:
        destination.unlink(missing_ok=True)
        raise DownloadError(f"Failed to write file: {e}") from e


def download_database(
    version: str | None = None, force: bool = False, show_progress: bool = True
) -> Path:
    """
    Download a release database into the cache and verify its checksum.

    Args:
        version: Release to download (``"v3.1.0"`` or ``"3.1.0"``). Defaults to
            ``INTERNACIA_DATA_VERSION`` if set, else the newest release with a supported
            contract major.
        force: Re-download even if the release is already cached.
        show_progress: Show a progress bar (requires the ``progress`` extra).

    Returns:
        Path to the cached ``internacia.duckdb``.

    Raises:
        DownloadError: If the download fails or the checksum does not match
        VersionError: If the version is invalid or no compatible release exists

    Example:
        >>> from internacia import download_database
        >>> db_path = download_database()
        >>> db_path = download_database(version="v3.0.0")
    """
    version = version or os.getenv(Config.ENV_DATA_VERSION)
    tag = release_tag(version) if version else get_latest_version()
    cache_path = get_cached_database_path(tag)
    if cache_path.exists() and not force:
        logger.info("Database %s already cached at: %s", tag, cache_path)
        return cache_path

    temp_path = cache_path.with_name(DB_FILE + ".tmp")
    _download_file(
        DOWNLOAD_URL.format(tag=tag, name=DB_FILE), temp_path, show_progress=show_progress
    )
    if temp_path.stat().st_size == 0:
        temp_path.unlink(missing_ok=True)
        raise DownloadError("Downloaded file is empty")

    checksums = _fetch_checksums(tag)
    if checksums is None:
        logger.warning("Release %s has no %s; the download was not verified", tag, CHECKSUMS_FILE)
    else:
        expected = checksums.get(DB_FILE)
        actual = _sha256(temp_path)
        if expected != actual:
            temp_path.unlink(missing_ok=True)
            raise DownloadError(
                f"{DB_FILE} from {tag} failed verification: sha256 {actual} != {expected}"
            )

    shutil.move(str(temp_path), str(cache_path))
    logger.info("Database %s downloaded to: %s", tag, cache_path)
    return cache_path


def check_for_updates() -> dict:
    """
    Compare the newest cached release with the newest compatible release.

    Returns:
        ``has_update`` (bool), ``current_version`` (tag or None), ``latest_version`` (tag),
        ``current_path`` (Path or None).

    Raises:
        DownloadError: If release information cannot be fetched
    """
    latest = get_latest_version()
    current = next(
        (tag for tag in cached_versions() if parse_version(tag)[0] == SUPPORTED_CONTRACT_MAJOR),  # type: ignore[index]
        None,
    )
    return {
        "has_update": current is None or parse_version(latest) > parse_version(current),  # type: ignore[operator]
        "current_version": current,
        "latest_version": latest,
        "current_path": get_cached_database_path(current) if current else None,
    }
