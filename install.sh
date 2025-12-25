#!/usr/bin/env bash
#
# Resolve Production Suite Installer
# Version: 0.2.0
# Platform: Linux (primary), macOS, Windows (WSL)
#
# Usage:
#   ./install.sh              # Interactive installation
#   ./install.sh --full       # Install with all optional extras
#   ./install.sh --minimal    # Install base only (no UI, no analysis)
#   ./install.sh --uninstall  # Remove installation
#   ./install.sh --help       # Show help
#

set -e

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "0.2.0")
VENV_DIR="$SCRIPT_DIR/.venv"
RPS_HOME="${RPS_HOME:-$HOME/.rps}"
MIN_PYTHON_VERSION="3.9"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# =============================================================================
# Helper Functions
# =============================================================================

print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║           Resolve Production Suite Installer v${VERSION}            ║"
    echo "║                                                                   ║"
    echo "║   Commercial-grade workflow automation for DaVinci Resolve        ║"
    echo "║                                                                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BOLD}${CYAN}>>> $1${NC}\n"
}

confirm() {
    local prompt="$1"
    local default="${2:-y}"

    if [[ "$default" == "y" ]]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi

    read -rp "$prompt" response
    response="${response:-$default}"
    [[ "$response" =~ ^[Yy]$ ]]
}

version_ge() {
    # Returns 0 if $1 >= $2
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# =============================================================================
# Prerequisite Checks
# =============================================================================

check_python() {
    log_step "Checking Python installation"

    # Try python3 first, then python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python not found. Please install Python ${MIN_PYTHON_VERSION}+"
        return 1
    fi

    # Check version
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

    if version_ge "$PYTHON_VERSION" "$MIN_PYTHON_VERSION"; then
        log_success "Python $PYTHON_VERSION found ($PYTHON_CMD)"
    else
        log_error "Python $PYTHON_VERSION found, but ${MIN_PYTHON_VERSION}+ is required"
        return 1
    fi

    # Check for venv module
    if ! $PYTHON_CMD -c "import venv" &> /dev/null; then
        log_error "Python venv module not found. Install with: sudo apt install python3-venv"
        return 1
    fi
    log_success "Python venv module available"

    return 0
}

check_pip() {
    log_step "Checking pip installation"

    if $PYTHON_CMD -m pip --version &> /dev/null; then
        PIP_VERSION=$($PYTHON_CMD -m pip --version | cut -d' ' -f2)
        log_success "pip $PIP_VERSION found"
        return 0
    else
        log_error "pip not found. Install with: sudo apt install python3-pip"
        return 1
    fi
}

detect_resolve() {
    log_step "Detecting DaVinci Resolve installation"

    RESOLVE_SCRIPT_PATH=""

    # Linux paths
    if [[ -d "/opt/resolve/Developer/Scripting/Modules" ]]; then
        RESOLVE_SCRIPT_PATH="/opt/resolve/Developer/Scripting/Modules"
        log_success "Found Resolve at: /opt/resolve"
    # Alternative Linux installation
    elif [[ -d "/opt/blackmagic/DaVinci Resolve/Developer/Scripting/Modules" ]]; then
        RESOLVE_SCRIPT_PATH="/opt/blackmagic/DaVinci Resolve/Developer/Scripting/Modules"
        log_success "Found Resolve at: /opt/blackmagic/DaVinci Resolve"
    # macOS path
    elif [[ -d "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules" ]]; then
        RESOLVE_SCRIPT_PATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
        log_success "Found Resolve at macOS system path"
    # Check environment variable
    elif [[ -n "$RESOLVE_SCRIPT_API" ]] && [[ -d "$RESOLVE_SCRIPT_API" ]]; then
        RESOLVE_SCRIPT_PATH="$RESOLVE_SCRIPT_API"
        log_success "Using RESOLVE_SCRIPT_API from environment: $RESOLVE_SCRIPT_API"
    else
        log_warning "DaVinci Resolve scripting modules not found automatically"
        log_info "Common locations:"
        log_info "  Linux: /opt/resolve/Developer/Scripting/Modules"
        log_info "  macOS: /Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
        log_info "  Windows: C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules"
        echo ""
        read -rp "Enter Resolve scripting modules path (or press Enter to skip): " RESOLVE_SCRIPT_PATH

        if [[ -n "$RESOLVE_SCRIPT_PATH" ]] && [[ ! -d "$RESOLVE_SCRIPT_PATH" ]]; then
            log_warning "Path does not exist. Continuing without Resolve API configuration."
            RESOLVE_SCRIPT_PATH=""
        fi
    fi

    return 0
}

check_dependencies() {
    log_step "Checking system dependencies"

    local missing_deps=()

    # Check for git (optional but recommended)
    if command -v git &> /dev/null; then
        log_success "git found"
    else
        log_warning "git not found (optional)"
    fi

    # Check for Qt dependencies (for UI)
    if [[ "$INSTALL_UI" == "true" ]]; then
        if command -v ldconfig &> /dev/null; then
            if ldconfig -p | grep -q libQt6; then
                log_success "Qt6 libraries found"
            else
                log_warning "Qt6 libraries may be missing. PySide6 will install its own."
            fi
        fi
    fi

    return 0
}

# =============================================================================
# Installation Functions
# =============================================================================

create_virtualenv() {
    log_step "Creating virtual environment"

    if [[ -d "$VENV_DIR" ]]; then
        if confirm "Virtual environment already exists. Recreate it?"; then
            rm -rf "$VENV_DIR"
        else
            log_info "Using existing virtual environment"
            return 0
        fi
    fi

    $PYTHON_CMD -m venv "$VENV_DIR"
    log_success "Virtual environment created at $VENV_DIR"
}

activate_venv() {
    source "$VENV_DIR/bin/activate"
    log_success "Virtual environment activated"
}

upgrade_pip() {
    log_step "Upgrading pip and build tools"

    pip install --upgrade pip setuptools wheel --quiet
    log_success "pip, setuptools, and wheel upgraded"
}

install_base_dependencies() {
    log_step "Installing base dependencies"

    pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
    log_success "Base dependencies installed (jsonschema>=4.18)"
}

install_package() {
    log_step "Installing Resolve Production Suite package"

    local extras=""

    if [[ "$INSTALL_UI" == "true" ]] && [[ "$INSTALL_ANALYSIS" == "true" ]]; then
        extras="[ui,analysis]"
    elif [[ "$INSTALL_UI" == "true" ]]; then
        extras="[ui]"
    elif [[ "$INSTALL_ANALYSIS" == "true" ]]; then
        extras="[analysis]"
    fi

    if [[ "$DEV_MODE" == "true" ]]; then
        pip install -e "${SCRIPT_DIR}${extras}" --quiet
        log_success "Package installed in development (editable) mode"
    else
        pip install "${SCRIPT_DIR}${extras}" --quiet
        log_success "Package installed"
    fi

    if [[ "$INSTALL_UI" == "true" ]]; then
        log_success "UI dependencies installed (PySide6)"
    fi

    if [[ "$INSTALL_ANALYSIS" == "true" ]]; then
        log_success "Analysis dependencies installed (OpenCV, NumPy)"
    fi
}

create_directories() {
    log_step "Creating data directories"

    mkdir -p "$RPS_HOME"/{logs,reports,presets,packs}

    log_success "Created: $RPS_HOME/logs"
    log_success "Created: $RPS_HOME/reports"
    log_success "Created: $RPS_HOME/presets"
    log_success "Created: $RPS_HOME/packs"
}

copy_sample_presets() {
    log_step "Installing sample presets and packs"

    if [[ -d "$SCRIPT_DIR/presets" ]]; then
        cp -n "$SCRIPT_DIR/presets/"*.json "$RPS_HOME/packs/" 2>/dev/null || true
        log_success "Sample packs copied to $RPS_HOME/packs/"
    fi
}

setup_environment() {
    log_step "Setting up environment variables"

    local shell_rc=""
    local shell_name=""

    # Detect shell
    if [[ -n "$ZSH_VERSION" ]] || [[ "$SHELL" == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
        shell_name="zsh"
    elif [[ -n "$BASH_VERSION" ]] || [[ "$SHELL" == *"bash"* ]]; then
        shell_rc="$HOME/.bashrc"
        shell_name="bash"
    else
        log_warning "Unknown shell. Please manually add environment variables."
        return 0
    fi

    # Create environment setup script
    local env_script="$SCRIPT_DIR/rps_env.sh"
    cat > "$env_script" << EOF
# Resolve Production Suite Environment
# Source this file or add to your shell rc file

export RPS_HOME="$RPS_HOME"
export PATH="\$PATH:$VENV_DIR/bin"
EOF

    if [[ -n "$RESOLVE_SCRIPT_PATH" ]]; then
        echo "export RESOLVE_SCRIPT_API=\"$RESOLVE_SCRIPT_PATH\"" >> "$env_script"
    fi

    log_success "Created environment script: $env_script"

    # Offer to add to shell rc
    if confirm "Add environment variables to $shell_rc?"; then
        echo "" >> "$shell_rc"
        echo "# Resolve Production Suite" >> "$shell_rc"
        echo "source \"$env_script\"" >> "$shell_rc"
        log_success "Environment variables added to $shell_rc"
        log_info "Run 'source $shell_rc' or restart your terminal to apply"
    else
        log_info "To activate environment, run: source $env_script"
    fi
}

create_launcher_script() {
    log_step "Creating launcher scripts"

    local bin_dir="$HOME/.local/bin"
    mkdir -p "$bin_dir"

    # Main CLI launcher
    cat > "$bin_dir/resolve-suite" << EOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
exec python -m cli.main "\$@"
EOF
    chmod +x "$bin_dir/resolve-suite"
    log_success "Created: $bin_dir/resolve-suite"

    # UI launcher (if installed)
    if [[ "$INSTALL_UI" == "true" ]]; then
        cat > "$bin_dir/resolve-suite-ui" << EOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
exec python -m ui.app "\$@"
EOF
        chmod +x "$bin_dir/resolve-suite-ui"
        log_success "Created: $bin_dir/resolve-suite-ui"
    fi

    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
        log_warning "$bin_dir is not in your PATH"
        log_info "Add to your shell rc: export PATH=\"\$PATH:$bin_dir\""
    fi
}

create_desktop_entry() {
    log_step "Creating desktop entry"

    if [[ "$INSTALL_UI" != "true" ]]; then
        log_info "Skipping desktop entry (UI not installed)"
        return 0
    fi

    local desktop_dir="$HOME/.local/share/applications"
    mkdir -p "$desktop_dir"

    cat > "$desktop_dir/resolve-production-suite.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Resolve Production Suite
Comment=Workflow automation for DaVinci Resolve
Exec=$HOME/.local/bin/resolve-suite-ui
Icon=applications-multimedia
Terminal=false
Categories=AudioVideo;Video;
Keywords=video;editing;resolve;davinci;
EOF

    log_success "Desktop entry created: $desktop_dir/resolve-production-suite.desktop"

    # Update desktop database if available
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$desktop_dir" 2>/dev/null || true
    fi
}

run_health_check() {
    log_step "Running health check"

    source "$VENV_DIR/bin/activate"

    if python "$SCRIPT_DIR/scripts/health_check.py"; then
        log_success "Health check passed"
    else
        log_warning "Health check reported issues (this may be normal if Resolve is not running)"
    fi
}

verify_installation() {
    log_step "Verifying installation"

    source "$VENV_DIR/bin/activate"

    # Check CLI is accessible
    if python -m cli.main list &> /dev/null; then
        log_success "CLI tools accessible"
    else
        log_warning "CLI tools may have issues"
    fi

    # List available tools
    echo ""
    log_info "Available tools:"
    python -m cli.main list 2>/dev/null || echo "  (Run 'resolve-suite list' to see tools)"
    echo ""
}

# =============================================================================
# Uninstall Function
# =============================================================================

uninstall() {
    print_banner
    log_step "Uninstalling Resolve Production Suite"

    if ! confirm "This will remove the virtual environment and launcher scripts. Continue?" "n"; then
        log_info "Uninstall cancelled"
        exit 0
    fi

    # Remove virtual environment
    if [[ -d "$VENV_DIR" ]]; then
        rm -rf "$VENV_DIR"
        log_success "Removed virtual environment"
    fi

    # Remove launcher scripts
    rm -f "$HOME/.local/bin/resolve-suite"
    rm -f "$HOME/.local/bin/resolve-suite-ui"
    log_success "Removed launcher scripts"

    # Remove desktop entry
    rm -f "$HOME/.local/share/applications/resolve-production-suite.desktop"
    log_success "Removed desktop entry"

    # Remove environment script
    rm -f "$SCRIPT_DIR/rps_env.sh"
    log_success "Removed environment script"

    if confirm "Also remove user data (~/.rps)?" "n"; then
        rm -rf "$RPS_HOME"
        log_success "Removed user data"
    else
        log_info "User data preserved at $RPS_HOME"
    fi

    echo ""
    log_success "Uninstall complete!"
    log_info "Note: You may need to manually remove 'source rps_env.sh' from your shell rc file"
}

# =============================================================================
# Help
# =============================================================================

show_help() {
    print_banner
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --full        Install with all optional extras (UI, analysis)"
    echo "  --minimal     Install base only (no UI, no analysis)"
    echo "  --dev         Install in development/editable mode"
    echo "  --uninstall   Remove the installation"
    echo "  --help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  RPS_HOME              Suite data directory (default: ~/.rps)"
    echo "  RESOLVE_SCRIPT_API    Path to Resolve scripting modules"
    echo ""
    echo "After Installation:"
    echo "  resolve-suite list              List all available tools"
    echo "  resolve-suite run <tool_id>     Run a specific tool"
    echo "  resolve-suite-ui                Launch the desktop application"
    echo ""
}

# =============================================================================
# Main Installation Flow
# =============================================================================

main() {
    # Parse arguments
    INSTALL_UI="ask"
    INSTALL_ANALYSIS="ask"
    DEV_MODE="false"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --full)
                INSTALL_UI="true"
                INSTALL_ANALYSIS="true"
                shift
                ;;
            --minimal)
                INSTALL_UI="false"
                INSTALL_ANALYSIS="false"
                shift
                ;;
            --dev)
                DEV_MODE="true"
                shift
                ;;
            --uninstall)
                uninstall
                exit 0
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    print_banner

    # Prerequisites
    check_python || exit 1
    check_pip || exit 1
    detect_resolve

    # Interactive options if not specified
    if [[ "$INSTALL_UI" == "ask" ]]; then
        echo ""
        if confirm "Install desktop UI (PySide6, ~150MB)?"; then
            INSTALL_UI="true"
        else
            INSTALL_UI="false"
        fi
    fi

    if [[ "$INSTALL_ANALYSIS" == "ask" ]]; then
        if confirm "Install analysis extras (OpenCV, NumPy for face/saliency detection)?"; then
            INSTALL_ANALYSIS="true"
        else
            INSTALL_ANALYSIS="false"
        fi
    fi

    check_dependencies

    # Installation
    echo ""
    log_step "Starting installation"
    echo "  - UI: $INSTALL_UI"
    echo "  - Analysis: $INSTALL_ANALYSIS"
    echo "  - Dev mode: $DEV_MODE"
    echo ""

    if ! confirm "Proceed with installation?"; then
        log_info "Installation cancelled"
        exit 0
    fi

    create_virtualenv
    activate_venv
    upgrade_pip
    install_base_dependencies
    install_package
    create_directories
    copy_sample_presets
    setup_environment
    create_launcher_script
    create_desktop_entry
    run_health_check
    verify_installation

    # Success message
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                   ║${NC}"
    echo -e "${GREEN}║              Installation Complete!                               ║${NC}"
    echo -e "${GREEN}║                                                                   ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    log_info "Quick Start:"
    echo "  1. Restart your terminal or run: source ~/.bashrc"
    echo "  2. List available tools: resolve-suite list"
    echo "  3. Run a tool: resolve-suite run t1_revision_resolver --dry-run"
    if [[ "$INSTALL_UI" == "true" ]]; then
        echo "  4. Launch UI: resolve-suite-ui"
    fi
    echo ""
    log_info "Documentation: $SCRIPT_DIR/docs/"
    log_info "Reports saved to: $RPS_HOME/reports/"
    echo ""
}

# Run main
main "$@"
