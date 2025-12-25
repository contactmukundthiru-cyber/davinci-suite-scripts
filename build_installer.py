#!/usr/bin/env python3
"""
Build standalone installer executables using PyInstaller.

This creates:
- Windows: Setup.exe (GUI installer)
- Linux: Setup (GUI installer)
- macOS: Setup.app (GUI installer)

Prerequisites:
    pip install pyinstaller

Usage:
    python build_installer.py          # Build for current platform
    python build_installer.py --all    # Build for all platforms (requires cross-compilation setup)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"
VERSION = (SCRIPT_DIR / "VERSION").read_text().strip() if (SCRIPT_DIR / "VERSION").exists() else "0.2.0"

# Files to include in the bundle
DATA_FILES = [
    ("VERSION", "."),
    ("README.md", "."),
    ("LICENSE", "."),
    ("requirements.txt", "."),
    ("pyproject.toml", "."),
    ("core", "core"),
    ("resolve", "resolve"),
    ("tools", "tools"),
    ("cli", "cli"),
    ("ui", "ui"),
    ("schemas", "schemas"),
    ("presets", "presets"),
    ("scripts", "scripts"),
    ("sample_data", "sample_data"),
    ("docs", "docs"),
]


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        return True


def build_installer():
    """Build the standalone installer executable."""
    print(f"\n{'='*60}")
    print(f"Building Resolve Production Suite Installer v{VERSION}")
    print(f"Platform: {platform.system()}")
    print(f"{'='*60}\n")

    # Prepare data files argument
    datas = []
    for src, dst in DATA_FILES:
        src_path = SCRIPT_DIR / src
        if src_path.exists():
            datas.append(f"--add-data={src_path}{os.pathsep}{dst}")

    # Determine output name based on platform
    if platform.system() == "Windows":
        name = "Setup"
        icon_arg = []  # Add --icon=path/to/icon.ico if you have one
    elif platform.system() == "Darwin":
        name = "Setup"
        icon_arg = []  # Add --icon=path/to/icon.icns if you have one
    else:
        name = "setup"
        icon_arg = []

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Single executable
        "--windowed",          # No console window (GUI app)
        f"--name={name}",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        "--clean",             # Clean build
        "--noconfirm",         # Don't ask for confirmation
    ] + icon_arg + datas + [
        str(SCRIPT_DIR / "installer_gui.py")
    ]

    print("Running PyInstaller...")
    print(f"Command: {' '.join(cmd[:10])}...")

    result = subprocess.run(cmd, cwd=SCRIPT_DIR)

    if result.returncode == 0:
        if platform.system() == "Windows":
            exe_path = DIST_DIR / "Setup.exe"
        elif platform.system() == "Darwin":
            exe_path = DIST_DIR / "Setup.app"
        else:
            exe_path = DIST_DIR / "setup"

        print(f"\n{'='*60}")
        print("BUILD SUCCESSFUL!")
        print(f"{'='*60}")
        print(f"\nOutput: {exe_path}")
        if exe_path.exists():
            size = exe_path.stat().st_size / (1024 * 1024)
            print(f"Size: {size:.1f} MB")
        print("\nThis executable can be distributed directly.")
        print("Users just double-click to install - no Python needed!")
    else:
        print("\nBuild failed!")
        sys.exit(1)


def build_cli():
    """Build standalone CLI executable."""
    print("\nBuilding CLI executable...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",  # Keep console for CLI
        "--name=resolve-suite",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        "--clean",
        "--noconfirm",
        "--add-data", f"{SCRIPT_DIR / 'VERSION'}{os.pathsep}.",
        "--add-data", f"{SCRIPT_DIR / 'core'}{os.pathsep}core",
        "--add-data", f"{SCRIPT_DIR / 'resolve'}{os.pathsep}resolve",
        "--add-data", f"{SCRIPT_DIR / 'tools'}{os.pathsep}tools",
        "--add-data", f"{SCRIPT_DIR / 'schemas'}{os.pathsep}schemas",
        "--add-data", f"{SCRIPT_DIR / 'scripts'}{os.pathsep}scripts",
        str(SCRIPT_DIR / "cli" / "main.py")
    ]

    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    if result.returncode == 0:
        print("CLI executable built successfully!")


def main():
    parser = argparse.ArgumentParser(description="Build standalone executables")
    parser.add_argument("--cli", action="store_true", help="Also build CLI executable")
    parser.add_argument("--clean", action="store_true", help="Clean build directories first")
    args = parser.parse_args()

    if args.clean:
        print("Cleaning build directories...")
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        for f in DIST_DIR.glob("Setup*"):
            f.unlink() if f.is_file() else shutil.rmtree(f)
        for f in DIST_DIR.glob("resolve-suite*"):
            f.unlink() if f.is_file() else shutil.rmtree(f)

    check_pyinstaller()
    build_installer()

    if args.cli:
        build_cli()


if __name__ == "__main__":
    main()
