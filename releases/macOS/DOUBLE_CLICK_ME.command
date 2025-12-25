#!/bin/bash
#
# Resolve Production Suite - macOS Installer
# Double-click this file to install
#

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear
echo ""
echo "========================================"
echo "  RESOLVE PRODUCTION SUITE INSTALLER"
echo "========================================"
echo ""
echo "This will install the suite on your Mac."
echo ""

# Function to check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
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
    echo "This takes about 2-3 minutes."
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

        # Download Python installer
        PYTHON_PKG="python-3.11.7-macos11.pkg"
        PYTHON_URL="https://www.python.org/ftp/python/3.11.7/$PYTHON_PKG"

        curl -L -o "/tmp/$PYTHON_PKG" "$PYTHON_URL" --progress-bar

        if [ ! -f "/tmp/$PYTHON_PKG" ]; then
            echo ""
            echo -e "${RED}[ERROR]${NC} Download failed!"
            echo ""
            echo "Please check your internet connection and try again."
            echo ""
            echo "Or download Python manually from:"
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
        echo "The Python installer will now open."
        echo "Please follow the installation prompts."
        echo ""

        # Open the installer
        open "/tmp/$PYTHON_PKG"

        echo "Waiting for Python installation to complete..."
        echo "(Close this window and run again after Python is installed)"
        echo ""
        read -p "Press Enter after Python is installed..."

        # Clean up
        rm -f "/tmp/$PYTHON_PKG"

        # Check again
        if check_python; then
            echo ""
            echo -e "${GREEN}[OK]${NC} Python installed successfully!"
        else
            echo ""
            echo -e "${YELLOW}[!]${NC} Python not detected yet."
            echo ""
            echo "Please close this window and double-click"
            echo "DOUBLE_CLICK_ME.command again after installation."
            echo ""
            read -p "Press Enter to exit..."
            exit 0
        fi
    fi
fi

echo ""
echo "Starting Resolve Production Suite installer..."
echo ""

# Run the Python installer
python3 installer.py

echo ""
read -p "Press Enter to close..."
