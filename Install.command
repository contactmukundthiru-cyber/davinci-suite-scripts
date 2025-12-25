#!/usr/bin/env bash
#
# Resolve Production Suite Installer
# macOS/Linux Smart Launcher
#
# Double-click (macOS) or run ./Install.command to start
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   Resolve Production Suite Installer${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check for standalone executable first
if [[ -f "$SCRIPT_DIR/dist/setup" ]]; then
    echo "Found standalone installer..."
    "$SCRIPT_DIR/dist/setup"
    exit 0
fi

if [[ -d "$SCRIPT_DIR/dist/Setup.app" ]]; then
    echo "Found standalone installer..."
    open "$SCRIPT_DIR/dist/Setup.app"
    exit 0
fi

# Detect OS
OS_TYPE="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
fi

# Find Python
find_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [[ $MAJOR -ge 3 ]] && [[ $MINOR -ge 9 ]]; then
            echo "python3"
            return 0
        fi
    fi

    if command -v python &> /dev/null; then
        PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [[ $MAJOR -ge 3 ]] && [[ $MINOR -ge 9 ]]; then
            echo "python"
            return 0
        fi
    fi

    return 1
}

# Check for tkinter
check_tkinter() {
    $1 -c "import tkinter" &> /dev/null
}

# Install Python based on OS
install_python() {
    echo ""
    echo -e "${YELLOW}Python 3.9+ is required but was not found.${NC}"
    echo ""

    if [[ "$OS_TYPE" == "macos" ]]; then
        echo "Options:"
        echo "  1. Install via Homebrew (recommended)"
        echo "  2. Open Python download page"
        echo "  3. Cancel"
        echo ""
        read -p "Enter choice (1-3): " CHOICE

        case $CHOICE in
            1)
                if command -v brew &> /dev/null; then
                    echo "Installing Python via Homebrew..."
                    brew install python python-tk
                    echo ""
                    echo -e "${GREEN}Python installed! Please run this installer again.${NC}"
                else
                    echo "Homebrew not found. Installing Homebrew first..."
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                    echo ""
                    echo "Homebrew installed. Now installing Python..."
                    brew install python python-tk
                    echo ""
                    echo -e "${GREEN}Python installed! Please run this installer again.${NC}"
                fi
                ;;
            2)
                open "https://www.python.org/downloads/"
                echo ""
                echo "After installing Python, run this installer again."
                ;;
            *)
                echo "Installation cancelled."
                exit 1
                ;;
        esac

    elif [[ "$OS_TYPE" == "linux" ]]; then
        echo "Options:"
        echo "  1. Install via package manager (requires sudo)"
        echo "  2. Open Python download page"
        echo "  3. Cancel"
        echo ""
        read -p "Enter choice (1-3): " CHOICE

        case $CHOICE in
            1)
                # Detect package manager
                if command -v apt &> /dev/null; then
                    echo "Installing Python via apt..."
                    sudo apt update
                    sudo apt install -y python3 python3-pip python3-venv python3-tk
                elif command -v dnf &> /dev/null; then
                    echo "Installing Python via dnf..."
                    sudo dnf install -y python3 python3-pip python3-tkinter
                elif command -v pacman &> /dev/null; then
                    echo "Installing Python via pacman..."
                    sudo pacman -S python python-pip tk
                elif command -v zypper &> /dev/null; then
                    echo "Installing Python via zypper..."
                    sudo zypper install -y python3 python3-pip python3-tk
                else
                    echo "Could not detect package manager."
                    echo "Please install Python 3.9+ manually."
                    exit 1
                fi
                echo ""
                echo -e "${GREEN}Python installed! Please run this installer again.${NC}"
                ;;
            2)
                if command -v xdg-open &> /dev/null; then
                    xdg-open "https://www.python.org/downloads/"
                else
                    echo "Visit: https://www.python.org/downloads/"
                fi
                echo ""
                echo "After installing Python, run this installer again."
                ;;
            *)
                echo "Installation cancelled."
                exit 1
                ;;
        esac
    fi

    read -p "Press Enter to exit..."
    exit 0
}

# Install tkinter
install_tkinter() {
    echo ""
    echo -e "${YELLOW}Tkinter not found. Installing...${NC}"
    echo ""

    if [[ "$OS_TYPE" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install python-tk
        else
            echo "Please install Tkinter using: brew install python-tk"
            echo "Or reinstall Python from python.org with Tcl/Tk support."
        fi
    elif [[ "$OS_TYPE" == "linux" ]]; then
        if command -v apt &> /dev/null; then
            sudo apt install -y python3-tk
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-tkinter
        elif command -v pacman &> /dev/null; then
            sudo pacman -S tk
        else
            echo "Please install python3-tk for your distribution."
        fi
    fi
}

# Main logic
PYTHON_CMD=$(find_python) || {
    install_python
    exit 0
}

echo -e "${GREEN}Found Python: $PYTHON_CMD${NC}"

# Check tkinter
if ! check_tkinter "$PYTHON_CMD"; then
    echo -e "${YELLOW}Tkinter not found.${NC}"
    read -p "Would you like to install it? (y/n): " INSTALL_TK
    if [[ "$INSTALL_TK" == "y" || "$INSTALL_TK" == "Y" ]]; then
        install_tkinter
        echo ""
        echo "Please run this installer again."
        read -p "Press Enter to exit..."
        exit 0
    else
        echo ""
        echo "You can use the command-line installer instead:"
        echo "  ./install.sh"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "Starting graphical installer..."
echo ""

$PYTHON_CMD "$SCRIPT_DIR/installer_gui.py"

EXIT_CODE=$?
if [[ $EXIT_CODE -ne 0 ]]; then
    echo ""
    echo -e "${YELLOW}Installation encountered an error.${NC}"
    echo ""
    echo "You can try the command-line installer:"
    echo "  ./install.sh"
    echo ""
    read -p "Press Enter to exit..."
fi
