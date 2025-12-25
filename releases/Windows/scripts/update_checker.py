#!/usr/bin/env python3
"""
Update Checker for Resolve Production Suite

Checks for new versions and optionally downloads updates.

Usage:
    python scripts/update_checker.py              # Check for updates
    python scripts/update_checker.py --download   # Download if available
    python scripts/update_checker.py --silent     # Exit code only (for scripts)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Tuple

# Configuration - Update these for your distribution
VERSION_CHECK_URL = os.environ.get(
    "RPS_VERSION_URL",
    "https://raw.githubusercontent.com/yourusername/resolve-production-suite/main/VERSION"
)
RELEASES_URL = os.environ.get(
    "RPS_RELEASES_URL",
    "https://github.com/yourusername/resolve-production-suite/releases"
)
GUMROAD_URL = os.environ.get(
    "RPS_GUMROAD_URL",
    "https://yourusername.gumroad.com/l/resolve-production-suite"
)

# For version info JSON (alternative to plain VERSION file)
VERSION_JSON_URL = os.environ.get(
    "RPS_VERSION_JSON_URL",
    ""  # Set this if using JSON version info
)


def get_local_version() -> str:
    """Get the locally installed version."""
    version_file = Path(__file__).parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.0.0"


def parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse version string into comparable tuple."""
    try:
        # Handle versions like "0.2.0", "1.0.0-beta", etc.
        clean = version_str.strip().split("-")[0]  # Remove -beta, -rc, etc.
        parts = clean.split(".")
        return tuple(int(p) for p in parts)
    except (ValueError, AttributeError):
        return (0, 0, 0)


def compare_versions(local: str, remote: str) -> int:
    """
    Compare two version strings.
    Returns: -1 if local < remote, 0 if equal, 1 if local > remote
    """
    local_tuple = parse_version(local)
    remote_tuple = parse_version(remote)

    if local_tuple < remote_tuple:
        return -1
    elif local_tuple > remote_tuple:
        return 1
    return 0


def fetch_remote_version() -> Optional[dict]:
    """
    Fetch version info from remote.
    Returns dict with 'version', 'changelog', 'download_url' if available.
    """
    # Try JSON endpoint first (more info)
    if VERSION_JSON_URL:
        try:
            req = urllib.request.Request(
                VERSION_JSON_URL,
                headers={"User-Agent": "ResolveProductionSuite-UpdateChecker"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data
        except (urllib.error.URLError, json.JSONDecodeError):
            pass

    # Fall back to plain VERSION file
    try:
        req = urllib.request.Request(
            VERSION_CHECK_URL,
            headers={"User-Agent": "ResolveProductionSuite-UpdateChecker"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            version = response.read().decode().strip()
            return {
                "version": version,
                "changelog": None,
                "download_url": GUMROAD_URL or RELEASES_URL
            }
    except urllib.error.URLError as e:
        return None


def check_for_updates(silent: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if updates are available.

    Returns:
        (update_available, remote_version, download_url)
    """
    local_version = get_local_version()

    if not silent:
        print(f"Current version: {local_version}")
        print("Checking for updates...")

    remote_info = fetch_remote_version()

    if remote_info is None:
        if not silent:
            print("Could not check for updates. Check your internet connection.")
        return False, None, None

    remote_version = remote_info.get("version", "0.0.0")
    download_url = remote_info.get("download_url", GUMROAD_URL)
    changelog = remote_info.get("changelog")

    comparison = compare_versions(local_version, remote_version)

    if comparison < 0:
        # Update available
        if not silent:
            print(f"\nUpdate available: v{remote_version}")
            if changelog:
                print(f"\nChangelog:\n{changelog}")
            print(f"\nDownload: {download_url}")
        return True, remote_version, download_url
    else:
        if not silent:
            print(f"You're up to date! (v{local_version})")
        return False, remote_version, download_url


def open_download_page(url: str) -> bool:
    """Open the download page in default browser."""
    import webbrowser
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check for Resolve Production Suite updates"
    )
    parser.add_argument(
        "--silent", "-s",
        action="store_true",
        help="Silent mode (exit code only: 0=up-to-date, 1=update available, 2=error)"
    )
    parser.add_argument(
        "--download", "-d",
        action="store_true",
        help="Open download page if update is available"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    update_available, remote_version, download_url = check_for_updates(
        silent=args.silent or args.json
    )

    if args.json:
        result = {
            "local_version": get_local_version(),
            "remote_version": remote_version,
            "update_available": update_available,
            "download_url": download_url
        }
        print(json.dumps(result, indent=2))

    if update_available and args.download:
        if download_url:
            print(f"\nOpening download page...")
            if not open_download_page(download_url):
                print(f"Could not open browser. Visit: {download_url}")

    # Exit codes
    if remote_version is None:
        sys.exit(2)  # Error checking
    elif update_available:
        sys.exit(1)  # Update available
    else:
        sys.exit(0)  # Up to date


if __name__ == "__main__":
    main()
