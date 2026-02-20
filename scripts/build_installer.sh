#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  P.S.AI — Build Installer Package                               ║
# ║  Packages the app into a distributable zip file.                 ║
# ║                                                                  ║
# ║  Usage: bash scripts/build_installer.sh                          ║
# ║  Output: dist/PSAI-<version>-<os>.zip                           ║
# ╚══════════════════════════════════════════════════════════════════╝

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

VERSION="0.1.0"

# Detect OS for zip naming
case "$(uname -s)" in
    Linux*)  OS_NAME="linux";;
    Darwin*) OS_NAME="macos";;
    *)       OS_NAME="unknown";;
esac

BUILD_DIR="$PROJECT_DIR/dist/psai-build"
ZIP_NAME="PSAI-${VERSION}-${OS_NAME}.zip"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  P.S.AI — Building Installer Package                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── Clean ─────────────────────────────────────────────────────────

echo "[1/4] Cleaning previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/P.S.AI"

# ── Copy source files ────────────────────────────────────────────

echo "[2/4] Copying application files..."

# Backend
mkdir -p "$BUILD_DIR/P.S.AI/backend"
cp -r "$PROJECT_DIR/backend/app" "$BUILD_DIR/P.S.AI/backend/app"
cp "$PROJECT_DIR/backend/pyproject.toml" "$BUILD_DIR/P.S.AI/backend/"
mkdir -p "$BUILD_DIR/P.S.AI/backend/data"

# Ontology (personas)
cp -r "$PROJECT_DIR/ontology" "$BUILD_DIR/P.S.AI/ontology"

# Scripts
mkdir -p "$BUILD_DIR/P.S.AI/scripts"
cp "$PROJECT_DIR/scripts/setup_models.sh" "$BUILD_DIR/P.S.AI/scripts/"

# Installer & launcher
cp "$PROJECT_DIR/install.sh" "$BUILD_DIR/P.S.AI/"
cp "$PROJECT_DIR/install.bat" "$BUILD_DIR/P.S.AI/"
cp "$PROJECT_DIR/launch.sh" "$BUILD_DIR/P.S.AI/"
cp "$PROJECT_DIR/launch.bat" "$BUILD_DIR/P.S.AI/"
chmod +x "$BUILD_DIR/P.S.AI/install.sh" "$BUILD_DIR/P.S.AI/launch.sh"

echo "  ✓ Files copied"

# ── Create README ────────────────────────────────────────────────

echo "[3/4] Creating README..."

cat > "$BUILD_DIR/P.S.AI/README.txt" << 'READMEEOF'
================================================================
  P.S.AI — Posthumous Social Artificial Intelligence
  Version 0.1.0
================================================================

WHAT IS THIS?

  P.S.AI lets you have philosophical dialogues with history's
  greatest thinkers — Socrates, Hypatia, Ada Lovelace, and more.
  Everything runs locally on your machine. No cloud. No accounts.

REQUIREMENTS

  - Python 3.11 or later  (https://www.python.org/downloads)
  - ~5 GB free disk space (for the AI model)
  - Internet connection    (for first-time model download only)

QUICK START

  Linux / macOS:
    1. Open a terminal in this folder
    2. Run:  bash install.sh
    3. Run:  bash launch.sh
    4. Open: http://localhost:8000/docs

  Windows:
    1. Double-click install.bat
    2. Double-click launch.bat
    3. Open: http://localhost:8000/docs

WHAT GETS INSTALLED?

  - A Python virtual environment (inside this folder, in .venv/)
  - Ollama (a local AI engine — https://ollama.com)
  - The llama3 language model (~4 GB download)

  Nothing is installed system-wide except Ollama.
  To uninstall, just delete this folder and uninstall Ollama.

ENVIRONMENT VARIABLES (optional)

  PSAI_MODEL   - Which AI model to use (default: llama3)
  PSAI_PORT    - Backend port (default: 8000)

TROUBLESHOOTING

  "Python is not installed"
    → Download from https://www.python.org/downloads
    → Windows: check "Add Python to PATH" during install

  "Ollama is not installed"
    → Download from https://ollama.com/download

  Backend won't start
    → Make sure port 8000 is not in use
    → Try: PSAI_PORT=8001 bash launch.sh

  Model download is slow
    → The first download is ~4 GB, subsequent starts are instant

================================================================
READMEEOF

echo "  ✓ README created"

# ── Zip it ───────────────────────────────────────────────────────

echo "[4/4] Creating zip archive..."

cd "$BUILD_DIR"
zip -rq "$PROJECT_DIR/dist/$ZIP_NAME" "P.S.AI"
cd "$PROJECT_DIR"

# Clean up build dir
rm -rf "$BUILD_DIR"

ZIP_SIZE=$(du -h "$PROJECT_DIR/dist/$ZIP_NAME" | cut -f1)

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Build complete!                                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  Output: dist/$ZIP_NAME"
echo "  Size:   $ZIP_SIZE"
echo ""
echo "  To distribute:"
echo "    1. Share the zip file"
echo "    2. Recipient extracts it"
echo "    3. Recipient runs install.sh (or install.bat on Windows)"
echo "    4. Recipient runs launch.sh (or launch.bat on Windows)"
echo ""
