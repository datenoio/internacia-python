"""Database downloader for internacia SDK, similar to NLTK's download mechanism."""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional

import requests
from internacia.config import Config
from internacia.exceptions import DownloadError, VersionError

logger = logging.getLogger(__name__)

# GitHub API endpoints
GITHUB_API_BASE = "https://api.github.com"
GITHUB_REPO = "datenoio/internacia-db"
GITHUB_RELEASES_URL = f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/releases"
GITHUB_LATEST_RELEASE_URL = f"{GITHUB_RELEASES_URL}/latest"


def get_cache_dir() -> Path:
    """
    Get the cache directory for downloaded databases.

    Priority:
    1. INTERNACIA_CACHE_DIR environment variable
    2. ~/.internacia/
    3. OS-specific cache directory

    Returns:
        Path to cache directory
    """
    # Check environment variable first
    env_cache = os.getenv(Config.ENV_CACHE_DIR)
    if env_cache:
        cache_dir = Path(env_cache).expanduser()
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    # Default to ~/.internacia/
    home_dir = Path.home()
    cache_dir = home_dir / ".internacia"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cached_database_path(version: Optional[str] = None) -> Path:
    """
    Get the path to the cached database file.

    Args:
        version: Optional version string. If None, uses 'latest'

    Returns:
        Path to cached database file
    """
    cache_dir = get_cache_dir()
    if version:
        # Versioned cache: ~/.internacia/v1.0.0/internacia.duckdb
        version_dir = cache_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        return version_dir / "internacia.duckdb"
    # Latest cache: ~/.internacia/internacia.duckdb
    return cache_dir / "internacia.duckdb"


def get_latest_version() -> str:
    """
    Fetch the latest release version from GitHub.

    Returns:
        Latest version string (e.g., "v1.0.0")

    Raises:
        DownloadError: If unable to fetch version information
        VersionError: If no releases found
    """
    try:
        logger.debug("Fetching latest release from: %s", GITHUB_LATEST_RELEASE_URL)
        response = requests.get(
            GITHUB_LATEST_RELEASE_URL,
            timeout=10,
            headers={"Accept": "application/vnd.github.v3+json"},
        )

        # Handle 404 specifically with a helpful error message
        if response.status_code == 404:
            error_msg = (
                f"Repository or release not found at {GITHUB_REPO}.\n"
                "This could mean:\n"
                "  1. The repository doesn't exist or has been renamed\n"
                "  2. The repository has no releases yet\n"
                "  3. The repository is private and requires authentication\n\n"
                "Alternative: You can build the database locally by:\n"
                "  1. Cloning the internacia-db repository\n"
                "  2. Running: python3 scripts/builder.py build --formats duckdb\n"
                "  3. Setting INTERNACIA_DB_PATH to point to the built database"
            )
            logger.error(error_msg)
            raise DownloadError(error_msg)

        response.raise_for_status()

        data = response.json()
        version = data.get("tag_name")

        if not version:
            raise VersionError("No version tag found in latest release")

        logger.info("Latest version: %s", version)
        return version

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            # Already handled above, but catch here for safety
            error_msg = (
                f"Repository or release not found at {GITHUB_REPO}.\n"
                "This could mean:\n"
                "  1. The repository doesn't exist or has been renamed\n"
                "  2. The repository has no releases yet\n"
                "  3. The repository is private and requires authentication\n\n"
                "Alternative: You can build the database locally by:\n"
                "  1. Cloning the internacia-db repository\n"
                "  2. Running: python3 scripts/builder.py build --formats duckdb\n"
                "  3. Setting INTERNACIA_DB_PATH to point to the built database"
            )
            logger.error(error_msg)
            raise DownloadError(error_msg) from e
        logger.error("Failed to fetch latest version: %s", str(e))
        raise DownloadError(f"Failed to fetch latest version: {e}") from e
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch latest version: %s", str(e))
        raise DownloadError(f"Failed to fetch latest version: {e}") from e
    except KeyError as e:
        logger.error("Invalid response format: %s", str(e))
        raise VersionError(f"Invalid release response format: {e}") from e


def get_database_info(version: Optional[str] = None) -> dict:
    """
    Get database metadata for a specific version.

    Args:
        version: Version string (e.g., "v1.0.0"). If None, uses latest.

    Returns:
        Dictionary with database metadata (size, download_url, etc.)

    Raises:
        DownloadError: If unable to fetch version information
        VersionError: If version not found
    """
    try:
        if version:
            # Fetch specific version
            url = f"{GITHUB_RELEASES_URL}/tags/{version}"
        else:
            # Fetch latest
            url = GITHUB_LATEST_RELEASE_URL

        logger.debug("Fetching release info from: %s", url)
        response = requests.get(
            url,
            timeout=10,
            headers={"Accept": "application/vnd.github.v3+json"},
        )

        # Handle 404 specifically with a helpful error message
        if response.status_code == 404:
            error_msg = (
                f"Release not found for {GITHUB_REPO}"
                + (f" (version: {version})" if version else "") + ".\n"
                "This could mean:\n"
                "  1. The repository doesn't exist or has been renamed\n"
                "  2. The specified version doesn't exist\n"
                "  3. The repository has no releases yet\n"
                "  4. The repository is private and requires authentication\n\n"
                "Alternative: You can build the database locally by:\n"
                "  1. Cloning the internacia-db repository\n"
                "  2. Running: python3 scripts/builder.py build --formats duckdb\n"
                "  3. Setting INTERNACIA_DB_PATH to point to the built database"
            )
            logger.error(error_msg)
            raise DownloadError(error_msg)

        response.raise_for_status()

        data = response.json()

        # Find database asset
        assets = data.get("assets", [])
        db_asset = None
        for asset in assets:
            if asset.get("name", "").endswith(".duckdb"):
                db_asset = asset
                break

        if not db_asset:
            release_tag = data.get("tag_name", version or "latest")
            asset_names = [asset.get("name", "") for asset in assets] if assets else []

            error_msg = (
                f"No database file (.duckdb) found in release {release_tag}.\n"
            )

            if assets:
                error_msg += (
                    f"Available assets in this release: {', '.join(asset_names) if asset_names else 'none'}\n"
                )
            else:
                error_msg += (
                    "This release has no assets attached.\n"
                )

            error_msg += (
                "\nThis could mean:\n"
                "  1. The database file hasn't been uploaded to this release yet\n"
                "  2. The database file is available in a different release\n"
                "  3. The database needs to be built from source\n\n"
                "Alternatives:\n"
                "  1. Check other releases for a database file:\n"
                "     from internacia import list_releases\n"
                "     releases = list_releases()\n"
                "     # Look for releases with has_database=True\n"
                "  2. Build the database locally:\n"
                "     - Clone the internacia-db repository\n"
                "     - Run: python3 scripts/builder.py build --formats duckdb\n"
                "     - Set INTERNACIA_DB_PATH to point to the built database\n"
                "  3. Use the source data directly from the repository"
            )

            logger.error(error_msg)
            raise VersionError(error_msg)

        return {
            "version": data.get("tag_name", version or "latest"),
            "name": db_asset.get("name"),
            "size": db_asset.get("size", 0),
            "download_url": db_asset.get("browser_download_url"),
            "content_type": db_asset.get("content_type"),
            "published_at": data.get("published_at"),
        }

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            # Already handled above, but catch here for safety
            error_msg = (
                f"Release not found for {GITHUB_REPO}"
                + (f" (version: {version})" if version else "") + ".\n"
                "This could mean:\n"
                "  1. The repository doesn't exist or has been renamed\n"
                "  2. The specified version doesn't exist\n"
                "  3. The repository has no releases yet\n"
                "  4. The repository is private and requires authentication\n\n"
                "Alternative: You can build the database locally by:\n"
                "  1. Cloning the internacia-db repository\n"
                "  2. Running: python3 scripts/builder.py build --formats duckdb\n"
                "  3. Setting INTERNACIA_DB_PATH to point to the built database"
            )
            logger.error(error_msg)
            raise DownloadError(error_msg) from e
        logger.error("Failed to fetch database info: %s", str(e))
        raise DownloadError(f"Failed to fetch database info: {str(e)}") from e
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch database info: %s", str(e))
        raise DownloadError(f"Failed to fetch database info: {str(e)}") from e
    except KeyError as e:
        logger.error("Invalid response format: %s", str(e))
        raise VersionError(f"Invalid release response format: {str(e)}") from e


def _download_file(url: str, destination: Path, show_progress: bool = True) -> None:
    """
    Download a file from URL to destination with progress bar.

    Args:
        url: URL to download from
        destination: Path to save the file
        show_progress: Whether to show progress bar

    Raises:
        DownloadError: If download fails
    """
    try:
        logger.info("Downloading from: %s", url)
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        # Try to use tqdm if available
        use_tqdm = False
        if show_progress:
            try:
                import tqdm  # pylint: disable=import-outside-toplevel
                use_tqdm = True
            except ImportError:
                pass

        destination.parent.mkdir(parents=True, exist_ok=True)

        # Download with progress
        if use_tqdm and total_size > 0:
            # tqdm is imported conditionally above
            import tqdm  # pylint: disable=import-outside-toplevel
            with open(destination, "wb") as f, tqdm.tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc="Downloading",
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        else:
            # Simple download without progress bar
            with open(destination, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        if show_progress and total_size > 0:
                            downloaded = f.tell()
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading: {percent:.1f}%", end="", flush=True)

            if show_progress and total_size > 0:
                print()  # New line after progress

        logger.info("Downloaded to: %s", destination)

    except requests.exceptions.RequestException as e:
        logger.error("Download failed: %s", str(e))
        # Clean up partial download
        if destination.exists():
            destination.unlink()
        raise DownloadError(f"Download failed: {str(e)}") from e
    except IOError as e:
        logger.error("Failed to write file: %s", str(e))
        raise DownloadError(f"Failed to write file: {str(e)}") from e


def download_database(
    version: Optional[str] = None,
    force: bool = False,
    show_progress: bool = True
) -> Path:
    """
    Download the database from GitHub releases.

    Similar to nltk.download(), this function downloads the database file
    and caches it locally.

    Args:
        version: Version to download (e.g., "v1.0.0"). If None, downloads latest.
        force: If True, re-download even if already cached
        show_progress: Whether to show download progress

    Returns:
        Path to downloaded database file

    Raises:
        DownloadError: If download fails
        VersionError: If version not found

    Example:
        >>> from internacia import download_database
        >>> db_path = download_database()  # Download latest
        >>> db_path = download_database(version="v1.0.0")  # Download specific version
    """
    try:
        # Get version info
        if version:
            logger.info("Downloading version: %s", version)
            db_info = get_database_info(version)
        else:
            logger.info("Downloading latest version")
            latest_version = get_latest_version()
            db_info = get_database_info(latest_version)
            version = db_info["version"]

        # Determine cache path
        cache_path = get_cached_database_path(version)

        # Check if already exists
        if cache_path.exists() and not force:
            logger.info("Database already cached at: %s", cache_path)
            return cache_path

        # Download
        download_url = db_info.get("download_url")
        if not download_url:
            raise DownloadError("No download URL found in release")

        # Download to temporary file first
        temp_path = cache_path.with_suffix(".duckdb.tmp")
        _download_file(download_url, temp_path, show_progress=show_progress)

        # Verify file exists and has content
        if not temp_path.exists() or temp_path.stat().st_size == 0:
            temp_path.unlink(missing_ok=True)
            raise DownloadError("Downloaded file is empty or missing")

        # Move to final location
        if cache_path.exists():
            cache_path.unlink()
        shutil.move(str(temp_path), str(cache_path))

        logger.info("Database downloaded successfully to: %s", cache_path)
        return cache_path

    except (DownloadError, VersionError):
        raise
    except Exception as e:
        logger.error("Unexpected error during download: %s", str(e))
        raise DownloadError(f"Unexpected error during download: {str(e)}") from e


def list_releases() -> list:
    """
    List all available releases and their database file status.

    Returns:
        List of dictionaries with release information:
        - tag_name: str, release tag
        - published_at: str, publication date
        - has_database: bool, whether release has a .duckdb file
        - asset_names: list, names of all assets in the release

    Raises:
        DownloadError: If unable to fetch releases
    """
    try:
        logger.debug("Fetching releases from: %s", GITHUB_RELEASES_URL)
        response = requests.get(
            GITHUB_RELEASES_URL,
            timeout=10,
            headers={"Accept": "application/vnd.github.v3+json"},
        )
        response.raise_for_status()

        releases_data = response.json()
        releases = []

        for release in releases_data:
            assets = release.get("assets", [])
            asset_names = [asset.get("name", "") for asset in assets]
            has_database = any(name.endswith(".duckdb") for name in asset_names)

            releases.append({
                "tag_name": release.get("tag_name", ""),
                "published_at": release.get("published_at", ""),
                "has_database": has_database,
                "asset_names": asset_names,
            })

        return releases

    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch releases: %s", str(e))
        raise DownloadError(f"Failed to fetch releases: {str(e)}") from e


def check_for_updates() -> dict:
    """
    Check if a newer database version is available.

    Returns:
        Dictionary with update information:
        - has_update: bool, whether update is available
        - current_version: str or None, current cached version
        - latest_version: str, latest available version
        - current_path: Path or None, path to current database
        - latest_info: dict, information about latest release

    Raises:
        DownloadError: If unable to check for updates
    """
    try:
        latest_version = get_latest_version()
        latest_info = get_database_info(latest_version)

        # Check for cached database
        cached_path = get_cached_database_path()
        current_version = None

        if cached_path.exists():
            # Try to determine version from cache
            # For now, we'll check if latest is newer by comparing timestamps
            # In a full implementation, we might store version metadata
            current_version = "cached"

        # For now, always suggest update if we can't determine current version
        # In a full implementation, compare versions properly
        has_update = True  # Conservative approach

        return {
            "has_update": has_update,
            "current_version": current_version,
            "latest_version": latest_version,
            "current_path": cached_path if cached_path.exists() else None,
            "latest_info": latest_info,
        }

    except Exception as e:
        logger.error("Failed to check for updates: %s", str(e))
        raise DownloadError(f"Failed to check for updates: {str(e)}") from e
