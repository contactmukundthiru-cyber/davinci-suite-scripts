#!/usr/bin/env bash
#
# Build a clean release archive for distribution (Gumroad, etc.)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "0.2.0")
RELEASE_NAME="resolve-production-suite-v${VERSION}"
DIST_DIR="$SCRIPT_DIR/dist"
ARCHIVE_PATH="$DIST_DIR/${RELEASE_NAME}.zip"

echo "Building release: $RELEASE_NAME"

# Create dist directory
mkdir -p "$DIST_DIR"

# Remove old archive if exists
rm -f "$ARCHIVE_PATH"

# Create the archive excluding development/unnecessary files
cd "$SCRIPT_DIR"

zip -r "$ARCHIVE_PATH" . \
    -x "*.git*" \
    -x "*__pycache__*" \
    -x "*.pyc" \
    -x "*.pyo" \
    -x ".venv/*" \
    -x "venv/*" \
    -x "*.egg-info/*" \
    -x "dist/*" \
    -x "build/*" \
    -x ".eggs/*" \
    -x "*.DS_Store" \
    -x "*.swp" \
    -x "*.swo" \
    -x "*~" \
    -x ".env" \
    -x ".env.*" \
    -x "*.log" \
    -x ".mypy_cache/*" \
    -x ".pytest_cache/*" \
    -x ".ruff_cache/*" \
    -x "htmlcov/*" \
    -x ".coverage" \
    -x "*.bak" \
    -x ".idea/*" \
    -x ".vscode/*" \
    -x "node_modules/*"

echo ""
echo "Release archive created:"
echo "  $ARCHIVE_PATH"
echo ""
echo "Size: $(du -h "$ARCHIVE_PATH" | cut -f1)"
echo ""
echo "Contents:"
unzip -l "$ARCHIVE_PATH" | tail -1
echo ""
echo "Ready to upload to Gumroad!"
