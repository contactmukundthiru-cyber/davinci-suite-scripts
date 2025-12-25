#!/usr/bin/env python3
"""
Package releases for Gumroad distribution.

Creates platform-specific zip files ready for upload.

Usage:
    python package_release.py

This creates:
    dist/
        ResolveProductionSuite-Windows.zip
        ResolveProductionSuite-macOS.zip
"""

import os
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
RELEASES_DIR = SCRIPT_DIR / "releases"
DIST_DIR = SCRIPT_DIR / "dist"
VERSION = (SCRIPT_DIR / "VERSION").read_text().strip() if (SCRIPT_DIR / "VERSION").exists() else "0.2.0"

# Source folders to include in packages
SOURCE_FOLDERS = ["cli", "core", "docs", "presets", "resolve", "sample_data", "schemas", "scripts", "tools", "ui"]
SOURCE_FILES = ["installer.py", "LICENSE", "README.md", "VERSION", "pyproject.toml", "requirements.txt"]


def clean_pycache(directory):
    """Remove all __pycache__ directories."""
    for pycache in directory.rglob("__pycache__"):
        shutil.rmtree(pycache)


def package_windows():
    """Package Windows release."""
    print("\n[Windows]")
    win_dir = RELEASES_DIR / "Windows"

    # Clean and recreate
    if win_dir.exists():
        shutil.rmtree(win_dir)
    win_dir.mkdir(parents=True)

    # Copy source files
    for folder in SOURCE_FOLDERS:
        src = SCRIPT_DIR / folder
        if src.exists():
            shutil.copytree(src, win_dir / folder)

    for file in SOURCE_FILES:
        src = SCRIPT_DIR / file
        if src.exists():
            shutil.copy2(src, win_dir / file)

    # Copy Windows-specific launcher
    launcher = SCRIPT_DIR / "releases" / "Windows" / "CLICK_ME_FIRST.bat"
    if not launcher.exists():
        # Create the launcher
        create_windows_launcher(win_dir)

    # Create README
    create_windows_readme(win_dir)

    # Clean pycache
    clean_pycache(win_dir)

    # Create zip
    zip_path = DIST_DIR / "ResolveProductionSuite-Windows.zip"
    if zip_path.exists():
        zip_path.unlink()

    shutil.make_archive(
        str(DIST_DIR / "ResolveProductionSuite-Windows"),
        'zip',
        RELEASES_DIR,
        "Windows"
    )
    print(f"  Created: dist/ResolveProductionSuite-Windows.zip")


def package_macos():
    """Package macOS release."""
    print("\n[macOS]")
    mac_dir = RELEASES_DIR / "macOS"

    # Clean and recreate
    if mac_dir.exists():
        shutil.rmtree(mac_dir)
    mac_dir.mkdir(parents=True)

    # Copy source files
    for folder in SOURCE_FOLDERS:
        src = SCRIPT_DIR / folder
        if src.exists():
            shutil.copytree(src, mac_dir / folder)

    for file in SOURCE_FILES:
        src = SCRIPT_DIR / file
        if src.exists():
            shutil.copy2(src, mac_dir / file)

    # Create macOS launcher
    create_macos_launcher(mac_dir)

    # Create README
    create_macos_readme(mac_dir)

    # Clean pycache
    clean_pycache(mac_dir)

    # Create zip
    zip_path = DIST_DIR / "ResolveProductionSuite-macOS.zip"
    if zip_path.exists():
        zip_path.unlink()

    shutil.make_archive(
        str(DIST_DIR / "ResolveProductionSuite-macOS"),
        'zip',
        RELEASES_DIR,
        "macOS"
    )
    print(f"  Created: dist/ResolveProductionSuite-macOS.zip")


def create_windows_launcher(dest_dir):
    """Create Windows batch launcher."""
    launcher = dest_dir / "CLICK_ME_FIRST.bat"
    launcher.write_text(r'''@echo off
setlocal EnableDelayedExpansion
title Resolve Production Suite - Windows Installer
color 0B

echo.
echo ========================================
echo   RESOLVE PRODUCTION SUITE INSTALLER
echo ========================================
echo.
echo This will install the suite on your Windows PC.
echo.
echo Checking if Python is installed...
echo.

REM First check common Python installation paths directly
set "PYTHON_PATH="

REM Check user Python installation (most common after fresh install)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :found_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :found_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :found_python
)

REM Check system-wide Python installation
if exist "C:\Python311\python.exe" (
    set "PYTHON_PATH=C:\Python311\python.exe"
    goto :found_python
)
if exist "C:\Python312\python.exe" (
    set "PYTHON_PATH=C:\Python312\python.exe"
    goto :found_python
)

REM Try py launcher (but check it's not the Microsoft Store stub)
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py -3 --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_PATH=py -3"
        goto :found_python
    )
)

REM Try python command
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python --version 2>&1 | findstr /C:"Python 3" >nul
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_PATH=python"
        goto :found_python
    )
)

REM Python not found - need to install
echo.
echo [!] Python is not installed on this computer.
echo.
echo I will download and install Python for you.
echo This takes about 2-3 minutes.
echo.
echo Press any key to start the download...
pause >nul

echo.
echo ========================================
echo   DOWNLOADING PYTHON
echo ========================================
echo.
echo Downloading Python 3.11 (about 25 MB)...
echo Please wait...
echo.

REM Download Python using PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Write-Host 'Downloading from python.org...'; try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile '%TEMP%\python_install.exe' -UseBasicParsing; Write-Host 'Download complete!' } catch { Write-Host 'Download failed!'; exit 1 } }"

if not exist "%TEMP%\python_install.exe" (
    echo.
    echo [ERROR] Download failed!
    echo.
    echo Please check your internet connection and try again.
    echo.
    echo Or download Python manually from:
    echo    https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During manual install, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALLING PYTHON
echo ========================================
echo.
echo Installing Python (this takes about 1 minute)...
echo Please wait...
echo.

REM Install Python with PATH
start /wait "" "%TEMP%\python_install.exe" /passive InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_tcltk=1 Include_launcher=1

REM Clean up installer
del "%TEMP%\python_install.exe" >nul 2>&1

REM Check if Python was installed successfully
set "PYTHON_PATH="
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
)

if defined PYTHON_PATH (
    echo.
    echo ========================================
    echo   PYTHON INSTALLED SUCCESSFULLY!
    echo ========================================
    echo.
    echo Found Python at: !PYTHON_PATH!
    echo.
    echo Starting the installer now...
    echo.
    timeout /t 2 >nul
    goto :run_installer
) else (
    echo.
    echo ========================================
    echo   PYTHON INSTALLED - RESTART REQUIRED
    echo ========================================
    echo.
    echo Python was installed but I couldn't find it yet.
    echo.
    echo Please do the following:
    echo    1. CLOSE this window
    echo    2. Double-click CLICK_ME_FIRST.bat again
    echo.
    echo Press any key to close...
    pause >nul
    exit /b 0
)

:found_python
echo [OK] Python found: !PYTHON_PATH!
echo.

:run_installer
cd /d "%~dp0"

echo Starting Resolve Production Suite installer...
echo.

if "!PYTHON_PATH!"=="py -3" (
    py -3 installer.py
) else (
    "!PYTHON_PATH!" installer.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] The installer encountered an issue.
    echo.
    echo If you see errors, try:
    echo    1. Right-click CLICK_ME_FIRST.bat
    echo    2. Select "Run as administrator"
    echo.
)

echo.
pause
endlocal
''')
    print("  Created: CLICK_ME_FIRST.bat")


def create_windows_readme(dest_dir):
    """Create Windows README."""
    readme = dest_dir / "README.txt"
    readme.write_text(f"""RESOLVE PRODUCTION SUITE v{VERSION} - WINDOWS
=============================================

HOW TO INSTALL:

1. Double-click "CLICK_ME_FIRST.bat"

2. If Python is not installed, it will download
   and install it automatically (takes 2-3 minutes)

3. Follow the on-screen menu to complete installation

That's it!


HOW TO USE THE TOOLS:

After installation, you can use the tools in two ways:

1. COMMAND LINE (recommended for automation):

   Open Command Prompt or PowerShell, then:

   resolve-suite list                    - See all available tools
   resolve-suite run t1_revision_resolver --dry-run  - Preview a tool
   resolve-suite run t6_timeline_normalizer          - Run a tool

2. DESKTOP UI:

   Double-click the desktop shortcut "Resolve Production Suite"
   Or run: resolve-suite-ui


THE 10 TOOLS:

1. Revision Resolver      - Swap assets while keeping appearance
2. Relink Across Projects - Update assets across multiple projects
3. Smart Reframer         - Convert 16:9 to 9:16, 1:1, etc.
4. Caption Layout         - Check caption safe zones
5. Feedback Compiler      - Convert feedback to timeline markers
6. Timeline Normalizer    - Check FPS, resolution, disabled clips
7. Component Graphics     - Manage reusable graphics library
8. Delivery Spec Enforcer - Validate render settings for YouTube, etc.
9. Change Impact Analyzer - Compare timeline versions
10. Brand Drift Detector  - Audit brand guideline compliance


DETAILED DOCUMENTATION:

See the docs folder for complete documentation:
- docs/USER_GUIDE.md      - Complete tool documentation
- docs/PRODUCTS.md        - Detailed specifications
- docs/QUICKSTART.md      - Quick start guide


TROUBLESHOOTING:

Q: It says "Windows protected your PC"
A: Click "More info" then "Run anyway"

Q: Download failed
A: Check your internet connection and try again

Q: Nothing happens when I double-click
A: Right-click the file and select "Run as administrator"


SUPPORT:
Email: contactmukundthiru@gmail.com
""")
    print("  Created: README.txt")


def create_macos_launcher(dest_dir):
    """Create macOS shell launcher."""
    launcher = dest_dir / "DOUBLE_CLICK_ME.command"
    launcher.write_text('''#!/bin/bash
#
# Resolve Production Suite - macOS Installer
# Double-click this file to install
#

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

clear
echo ""
echo "========================================"
echo "  RESOLVE PRODUCTION SUITE INSTALLER"
echo "========================================"
echo ""
echo "This will install the suite on your Mac."
echo ""

# Global variable for Python command
PYTHON_CMD=""

# Function to find Python in common locations
find_python() {
    # Check Python framework location (installed via pkg)
    if [ -x "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3" ]; then
        PYTHON_CMD="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
        return 0
    fi
    if [ -x "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3" ]; then
        PYTHON_CMD="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
        return 0
    fi
    # Check Homebrew locations
    if [ -x "/opt/homebrew/bin/python3" ]; then
        PYTHON_CMD="/opt/homebrew/bin/python3"
        return 0
    fi
    if [ -x "/usr/local/bin/python3" ]; then
        PYTHON_CMD="/usr/local/bin/python3"
        return 0
    fi
    # Check PATH
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        return 0
    fi
    return 1
}

# Function to check Python version
check_python() {
    if find_python; then
        PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
            return 0
        fi
    fi
    return 1
}

# Check for Python
echo "Checking if Python is installed..."
echo ""

if check_python; then
    echo -e "${GREEN}[OK]${NC} Python $PYTHON_VERSION found!"
    echo ""
else
    echo -e "${YELLOW}[!]${NC} Python 3.9+ is not installed."
    echo ""
    echo "I will download and install Python for you."
    echo ""

    # Check if Homebrew is available
    if command -v brew &> /dev/null; then
        echo "Homebrew detected. Installing Python via Homebrew..."
        echo ""
        brew install python@3.11

        if check_python; then
            echo ""
            echo -e "${GREEN}[OK]${NC} Python installed successfully!"
        else
            echo -e "${RED}[ERROR]${NC} Installation failed."
            echo ""
            echo "Please install Python manually from:"
            echo "  https://www.python.org/downloads/"
            echo ""
            read -p "Press Enter to exit..."
            exit 1
        fi
    else
        echo "Downloading Python from python.org..."
        echo ""

        # Download Python installer - use universal2 package for M1/Intel compatibility
        PYTHON_PKG="python-3.11.9-macos11.pkg"
        PYTHON_URL="https://www.python.org/ftp/python/3.11.9/$PYTHON_PKG"

        echo "Downloading from: $PYTHON_URL"
        curl -L -o "/tmp/$PYTHON_PKG" "$PYTHON_URL" --progress-bar

        if [ ! -f "/tmp/$PYTHON_PKG" ] || [ ! -s "/tmp/$PYTHON_PKG" ]; then
            echo ""
            echo -e "${RED}[ERROR]${NC} Download failed!"
            echo ""
            echo "Please download Python manually from:"
            echo "  https://www.python.org/downloads/"
            echo ""
            read -p "Press Enter to exit..."
            exit 1
        fi

        echo ""
        echo "========================================"
        echo "  INSTALLING PYTHON"
        echo "========================================"
        echo ""
        echo "Installing Python (you may need to enter your password)..."
        echo ""

        # Install using sudo installer for silent installation
        sudo installer -pkg "/tmp/$PYTHON_PKG" -target /

        INSTALL_RESULT=$?

        # Clean up
        rm -f "/tmp/$PYTHON_PKG"

        if [ $INSTALL_RESULT -ne 0 ]; then
            echo ""
            echo -e "${RED}[ERROR]${NC} Installation failed!"
            echo ""
            echo "Please download and install Python manually from:"
            echo "  https://www.python.org/downloads/"
            echo ""
            read -p "Press Enter to exit..."
            exit 1
        fi

        # Check again
        if check_python; then
            echo ""
            echo -e "${GREEN}[OK]${NC} Python installed successfully!"
        else
            echo ""
            echo -e "${YELLOW}[!]${NC} Python may require a new terminal session."
            echo ""
            echo "Please close this window and double-click"
            echo "DOUBLE_CLICK_ME.command again."
            echo ""
            read -p "Press Enter to exit..."
            exit 0
        fi
    fi
fi

echo ""
echo "Starting Resolve Production Suite installer..."
echo ""

# Run the Python installer using the found Python
$PYTHON_CMD installer.py

echo ""
read -p "Press Enter to close..."
''')
    launcher.chmod(0o755)
    print("  Created: DOUBLE_CLICK_ME.command")


def create_macos_readme(dest_dir):
    """Create macOS README."""
    readme = dest_dir / "README.txt"
    readme.write_text(f"""RESOLVE PRODUCTION SUITE v{VERSION} - MACOS
===========================================

HOW TO INSTALL:

1. Double-click "DOUBLE_CLICK_ME.command"

2. If you see "unidentified developer" warning:
   - Right-click > Open > Open
   - Or: System Preferences > Security > Open Anyway

3. If Python is not installed, it will download
   and install it automatically

4. Follow the on-screen menu to complete installation

That's it!


HOW TO USE THE TOOLS:

After installation, you can use the tools in two ways:

1. COMMAND LINE (recommended for automation):

   Open Terminal, then:

   resolve-suite list                    - See all available tools
   resolve-suite run t1_revision_resolver --dry-run  - Preview a tool
   resolve-suite run t6_timeline_normalizer          - Run a tool

2. DESKTOP UI:

   Double-click the desktop alias "Resolve Production Suite"
   Or run: resolve-suite-ui


THE 10 TOOLS:

1. Revision Resolver      - Swap assets while keeping appearance
2. Relink Across Projects - Update assets across multiple projects
3. Smart Reframer         - Convert 16:9 to 9:16, 1:1, etc.
4. Caption Layout         - Check caption safe zones
5. Feedback Compiler      - Convert feedback to timeline markers
6. Timeline Normalizer    - Check FPS, resolution, disabled clips
7. Component Graphics     - Manage reusable graphics library
8. Delivery Spec Enforcer - Validate render settings for YouTube, etc.
9. Change Impact Analyzer - Compare timeline versions
10. Brand Drift Detector  - Audit brand guideline compliance


DETAILED DOCUMENTATION:

See the docs folder for complete documentation:
- docs/USER_GUIDE.md      - Complete tool documentation
- docs/PRODUCTS.md        - Detailed specifications
- docs/QUICKSTART.md      - Quick start guide


TROUBLESHOOTING:

Q: "unidentified developer" warning
A: Right-click > Open > Open

Q: Terminal says "permission denied"
A: Open Terminal, run: chmod +x DOUBLE_CLICK_ME.command

Q: Download failed
A: Check your internet connection and try again


SUPPORT:
Email: contactmukundthiru@gmail.com
""")
    print("  Created: README.txt")


def main():
    print(f"\nPackaging Resolve Production Suite v{VERSION}")
    print("=" * 50)

    # Ensure dist directory exists
    DIST_DIR.mkdir(exist_ok=True)

    # Package both platforms
    package_windows()
    package_macos()

    print("\n" + "=" * 50)
    print("DONE! Ready for Gumroad upload:")
    print("=" * 50)
    print(f"""
  dist/ResolveProductionSuite-Windows.zip
  dist/ResolveProductionSuite-macOS.zip

Upload each zip to Gumroad as a separate file,
or create separate products for each platform.
""")


if __name__ == "__main__":
    main()
