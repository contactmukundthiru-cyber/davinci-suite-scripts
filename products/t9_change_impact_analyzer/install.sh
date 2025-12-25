#!/usr/bin/env bash
#
# Standalone Tool Installer Template
# Copy this to each product directory and customize TOOL_NAME and TOOL_ID
#

set -e

# =============================================================================
# CUSTOMIZE THESE FOR EACH TOOL
# =============================================================================
TOOL_NAME="Change Impact Analyzer"           # e.g., "Revision Resolver"
TOOL_ID="t9_change_impact_analyzer"  # e.g., "t1_revision_resolver"
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "0.2.0")
VENV_DIR="$SCRIPT_DIR/.venv"
MIN_PYTHON_VERSION="3.9"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${BOLD}${CYAN}>>> $1${NC}\n"; }

print_banner() {
    echo -e "${CYAN}"
    echo "======================================================================="
    echo "  ${TOOL_NAME} Installer v${VERSION}"
    echo "  Part of Resolve Production Suite"
    echo "======================================================================="
    echo -e "${NC}"
}

check_python() {
    log_step "Checking Python installation"

    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python not found. Please install Python ${MIN_PYTHON_VERSION}+"
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    log_success "Python $PYTHON_VERSION found"
}

detect_resolve() {
    log_step "Detecting DaVinci Resolve"

    RESOLVE_SCRIPT_PATH=""

    if [[ -d "/opt/resolve/Developer/Scripting/Modules" ]]; then
        RESOLVE_SCRIPT_PATH="/opt/resolve/Developer/Scripting/Modules"
    elif [[ -n "$RESOLVE_SCRIPT_API" ]] && [[ -d "$RESOLVE_SCRIPT_API" ]]; then
        RESOLVE_SCRIPT_PATH="$RESOLVE_SCRIPT_API"
    elif [[ -d "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules" ]]; then
        RESOLVE_SCRIPT_PATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
    fi

    if [[ -n "$RESOLVE_SCRIPT_PATH" ]]; then
        log_success "Found Resolve at: $RESOLVE_SCRIPT_PATH"
    else
        log_warning "Resolve not auto-detected. Set RESOLVE_SCRIPT_API environment variable."
    fi
}

install() {
    print_banner
    check_python
    detect_resolve

    log_step "Creating virtual environment"
    $PYTHON_CMD -m venv "$VENV_DIR"
    log_success "Virtual environment created"

    log_step "Installing dependencies"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel --quiet
    pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
    pip install -e "$SCRIPT_DIR" --quiet
    log_success "Dependencies installed"

    log_step "Creating launcher script"
    cat > "$SCRIPT_DIR/run.sh" << EOF
#!/usr/bin/env bash
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
source "\$SCRIPT_DIR/.venv/bin/activate"
export RESOLVE_SCRIPT_API="${RESOLVE_SCRIPT_PATH:-\$RESOLVE_SCRIPT_API}"
python "\$SCRIPT_DIR/run_tool.py" "\$@"
EOF
    chmod +x "$SCRIPT_DIR/run.sh"
    log_success "Created: $SCRIPT_DIR/run.sh"

    echo ""
    echo -e "${GREEN}Installation complete!${NC}"
    echo ""
    echo "Usage:"
    echo "  ./run.sh --options sample_data/options.json --dry-run"
    echo "  ./run.sh --help"
    echo ""
}

uninstall() {
    print_banner
    log_step "Uninstalling ${TOOL_NAME}"

    rm -rf "$VENV_DIR"
    rm -f "$SCRIPT_DIR/run.sh"

    log_success "Uninstall complete"
}

case "${1:-}" in
    --uninstall)
        uninstall
        ;;
    --help|-h)
        print_banner
        echo "Usage: ./install.sh [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --uninstall   Remove the installation"
        echo "  --help        Show this help"
        ;;
    *)
        install
        ;;
esac
