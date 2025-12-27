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
