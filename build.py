#!/usr/bin/env python3
"""
Build standalone installer for Resolve Production Suite.

Usage:
    python build.py          # Build for current platform
    python build.py --clean  # Clean build first

Output:
    Windows: dist/ResolveProductionSuite-Setup.exe
    macOS:   dist/ResolveProductionSuite-Setup (or .app)
    Linux:   dist/ResolveProductionSuite-Setup

Requirements:
    pip install pyinstaller
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()


def main():
    # Clean if requested
    if "--clean" in sys.argv:
        print("Cleaning...")
        shutil.rmtree(SCRIPT_DIR / "build", ignore_errors=True)
        shutil.rmtree(SCRIPT_DIR / "dist", ignore_errors=True)
        for f in SCRIPT_DIR.glob("*.spec"):
            f.unlink()

    # Check/install PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Platform-specific settings
    system = platform.system()
    if system == "Windows":
        name = "ResolveProductionSuite-Setup"
        sep = ";"
    elif system == "Darwin":
        name = "ResolveProductionSuite-Setup"
        sep = ":"
    else:
        name = "ResolveProductionSuite-Setup"
        sep = ":"

    # Build command
    data_args = []
    data_items = [
        "VERSION", "README.md", "LICENSE", "requirements.txt", "pyproject.toml",
        "core", "resolve", "tools", "cli", "ui", "schemas", "presets", "scripts",
        "sample_data", "docs"
    ]

    for item in data_items:
        src = SCRIPT_DIR / item
        if src.exists():
            dest = "." if src.is_file() else item
            data_args.extend(["--add-data", f"{src}{sep}{dest}"])

    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(SCRIPT_DIR / "installer.py"),
        "--onefile",
        "--console",
        f"--name={name}",
        "--clean",
        "--noconfirm",
    ] + data_args

    print(f"\nBuilding for {system}...")
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)

    if result.returncode == 0:
        if system == "Windows":
            output = SCRIPT_DIR / "dist" / f"{name}.exe"
        else:
            output = SCRIPT_DIR / "dist" / name

        print(f"\n{'='*50}")
        print("BUILD SUCCESSFUL!")
        print(f"{'='*50}")
        print(f"\nOutput: {output}")
        if output.exists():
            size = output.stat().st_size / (1024 * 1024)
            print(f"Size: {size:.1f} MB")
        print("\nThis is your standalone installer!")
        print("Users just double-click - no Python needed.")
    else:
        print("\nBuild failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
