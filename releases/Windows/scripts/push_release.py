#!/usr/bin/env python3
"""
Push a new release to GitHub.

Usage:
    python scripts/push_release.py 0.3.0 "Bug fixes and improvements"

This will:
1. Update VERSION file
2. Update version.json
3. Rebuild packages (calls package_release.py)
4. Create git tag
5. Push to GitHub
6. Create GitHub release with zip files attached

Requirements:
    - gh CLI installed and authenticated (https://cli.github.com/)
    - Git configured with push access
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent

# GitHub repo info
GITHUB_USER = "contactmukundthiru-cyber"
GITHUB_REPO = "davinci-suite-scripts"


def run(cmd, check=True, capture=False):
    """Run a shell command."""
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, check=check, capture_output=capture, text=True)
    return result.stdout.strip() if capture else None


def update_version(new_version):
    """Update VERSION file."""
    version_file = PROJECT_DIR / "VERSION"
    version_file.write_text(new_version + "\n")
    print(f"  Updated VERSION to {new_version}")


def update_version_json(new_version, changelog):
    """Update version.json file."""
    json_file = PROJECT_DIR / "version.json"

    data = {
        "version": new_version,
        "release_date": date.today().isoformat(),
        "min_python": "3.9",
        "changelog": changelog,
        "download_url": f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest",
        "windows_url": f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download/ResolveProductionSuite-Windows.zip",
        "macos_url": f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download/ResolveProductionSuite-macOS.zip",
        "support_email": "contactmukundthiru@gmail.com"
    }

    json_file.write_text(json.dumps(data, indent=2) + "\n")
    print(f"  Updated version.json")


def update_installer_version(new_version):
    """Update VERSION in installer.py."""
    installer_file = PROJECT_DIR / "installer.py"
    content = installer_file.read_text()

    # Replace VERSION = "x.x.x" with new version
    import re
    content = re.sub(
        r'VERSION = "[^"]*"',
        f'VERSION = "{new_version}"',
        content
    )

    installer_file.write_text(content)
    print(f"  Updated installer.py VERSION")


def build_packages():
    """Run package_release.py to build packages."""
    print("\nBuilding packages...")
    run(f"cd {PROJECT_DIR} && python package_release.py")


def git_commit_and_tag(version, changelog):
    """Commit changes and create tag."""
    print("\nCommitting changes...")
    run(f'cd {PROJECT_DIR} && git add VERSION version.json installer.py')
    run(f'cd {PROJECT_DIR} && git commit -m "Release v{version}: {changelog}"')

    print(f"\nCreating tag v{version}...")
    run(f'cd {PROJECT_DIR} && git tag -a v{version} -m "{changelog}"')


def push_to_github():
    """Push commits and tags to GitHub."""
    print("\nPushing to GitHub...")
    run(f"cd {PROJECT_DIR} && git push origin main")
    run(f"cd {PROJECT_DIR} && git push origin --tags")


def create_github_release(version, changelog):
    """Create GitHub release with assets."""
    print("\nCreating GitHub release...")

    windows_zip = PROJECT_DIR / "dist" / "ResolveProductionSuite-Windows.zip"
    macos_zip = PROJECT_DIR / "dist" / "ResolveProductionSuite-macOS.zip"

    # Build release notes
    notes = f"""## Resolve Production Suite v{version}

{changelog}

### Downloads
- **Windows**: ResolveProductionSuite-Windows.zip
- **macOS**: ResolveProductionSuite-macOS.zip

### Installation
1. Download the zip for your platform
2. Extract the folder
3. **Windows**: Double-click `CLICK_ME_FIRST.bat`
4. **macOS**: Double-click `DOUBLE_CLICK_ME.command`

### What's Included
10 workflow automation tools for DaVinci Resolve:
1. Revision Resolver
2. Relink Across Projects
3. Smart Reframer
4. Caption Layout Protector
5. Feedback Compiler
6. Timeline Normalizer
7. Component Graphics
8. Delivery Spec Enforcer
9. Change Impact Analyzer
10. Brand Drift Detector
"""

    # Create temp file for notes
    notes_file = PROJECT_DIR / "dist" / "release_notes.md"
    notes_file.write_text(notes)

    # Create release using gh CLI
    assets = []
    if windows_zip.exists():
        assets.append(str(windows_zip))
    if macos_zip.exists():
        assets.append(str(macos_zip))

    assets_str = " ".join([f'"{a}"' for a in assets])

    run(f'cd {PROJECT_DIR} && gh release create v{version} {assets_str} --title "v{version}" --notes-file dist/release_notes.md')

    # Clean up
    notes_file.unlink()

    print(f"\n✅ Release v{version} created successfully!")
    print(f"   https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/tag/v{version}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/push_release.py <version> <changelog>")
        print('Example: python scripts/push_release.py 0.3.0 "Bug fixes and performance improvements"')
        sys.exit(1)

    new_version = sys.argv[1]
    changelog = sys.argv[2]

    print(f"\n{'='*60}")
    print(f"  Pushing Release v{new_version}")
    print(f"  Changelog: {changelog}")
    print(f"{'='*60}\n")

    # Confirm
    confirm = input("Proceed? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)

    print("\n1. Updating version files...")
    update_version(new_version)
    update_version_json(new_version, changelog)
    update_installer_version(new_version)

    print("\n2. Building packages...")
    build_packages()

    print("\n3. Git commit and tag...")
    git_commit_and_tag(new_version, changelog)

    print("\n4. Pushing to GitHub...")
    push_to_github()

    print("\n5. Creating GitHub release...")
    create_github_release(new_version, changelog)

    print(f"""
{'='*60}
  RELEASE COMPLETE!
{'='*60}

Beta testers will now see update v{new_version} available.
They can update directly from the app without downloading a new zip!

To verify:
  1. Open: https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases
  2. Check that v{new_version} is listed with both zip files

""")


if __name__ == "__main__":
    main()
