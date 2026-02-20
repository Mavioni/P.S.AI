#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  P.S.AI — Installer                                             ║
# ║  Run this once after extracting the zip.                         ║
# ║  Usage: bash install.sh                                          ║
# ╚══════════════════════════════════════════════════════════════════╝

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODEL="${PSAI_MODEL:-llama3}"
VENV_DIR="$SCRIPT_DIR/.venv"

banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}P.S.AI — Posthumous Social Artificial Intelligence${NC}         ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}Installer${NC}                                                  ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }
info() { echo -e "  ${YELLOW}→${NC} $1"; }
step() { echo -e "\n${BOLD}[$1/$TOTAL_STEPS] $2${NC}"; }

TOTAL_STEPS=5

# ── Detect OS ─────────────────────────────────────────────────────

detect_os() {
    case "$(uname -s)" in
        Linux*)  OS="linux";;
        Darwin*) OS="mac";;
        *)       OS="unknown";;
    esac
    echo "$OS"
}

# ── Step 1: Check Python ─────────────────────────────────────────

check_python() {
    step 1 "Checking Python..."

    # Try python3 first, then python
    if command -v python3 &>/dev/null; then
        PYTHON="python3"
    elif command -v python &>/dev/null; then
        PYTHON="python"
    else
        fail "Python is not installed."
        echo ""
        echo "    Please install Python 3.11 or later:"
        echo ""
        OS=$(detect_os)
        if [ "$OS" = "mac" ]; then
            echo "      brew install python@3.12"
            echo "      — or —"
            echo "      Download from https://www.python.org/downloads/"
        elif [ "$OS" = "linux" ]; then
            echo "      sudo apt install python3 python3-venv python3-pip   (Debian/Ubuntu)"
            echo "      sudo dnf install python3                            (Fedora)"
        fi
        echo ""
        exit 1
    fi

    # Check version >= 3.11
    PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PY_MAJOR=$($PYTHON -c 'import sys; print(sys.version_info.major)')
    PY_MINOR=$($PYTHON -c 'import sys; print(sys.version_info.minor)')

    if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
        fail "Python $PY_VERSION found, but P.S.AI requires Python 3.11+."
        echo "    Please upgrade Python and re-run this installer."
        exit 1
    fi

    ok "Python $PY_VERSION ($PYTHON)"
}

# ── Step 2: Create virtual environment & install backend ──────────

setup_backend() {
    step 2 "Setting up Python backend..."

    if [ ! -d "$VENV_DIR" ]; then
        info "Creating virtual environment..."
        $PYTHON -m venv "$VENV_DIR"
    fi

    # Activate venv
    source "$VENV_DIR/bin/activate"

    info "Installing backend dependencies (this may take a minute)..."
    pip install --quiet --upgrade pip
    pip install --quiet "$SCRIPT_DIR/backend[security]"

    ok "Backend installed in virtual environment"
}

# ── Step 3: Install Ollama ────────────────────────────────────────

install_ollama() {
    step 3 "Checking Ollama (local AI engine)..."

    if command -v ollama &>/dev/null; then
        OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
        ok "Ollama is already installed ($OLLAMA_VERSION)"
        return
    fi

    info "Ollama is not installed. Installing now..."
    OS=$(detect_os)

    if [ "$OS" = "mac" ]; then
        if command -v brew &>/dev/null; then
            info "Installing via Homebrew..."
            brew install ollama
        else
            info "Downloading Ollama installer..."
            curl -fsSL https://ollama.com/install.sh | sh
        fi
    elif [ "$OS" = "linux" ]; then
        info "Downloading Ollama installer..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        fail "Could not auto-install Ollama on this OS."
        echo "    Please install manually from: https://ollama.com/download"
        exit 1
    fi

    if command -v ollama &>/dev/null; then
        ok "Ollama installed successfully"
    else
        fail "Ollama installation failed."
        echo "    Please install manually from: https://ollama.com/download"
        exit 1
    fi
}

# ── Step 4: Pull the LLM model ───────────────────────────────────

pull_model() {
    step 4 "Downloading AI model ($MODEL)..."
    info "This downloads ~4 GB on first run. Please be patient."

    # Start Ollama in the background if it's not running
    if ! curl -sf http://localhost:11434/api/tags &>/dev/null; then
        info "Starting Ollama server..."
        ollama serve &>/dev/null &
        OLLAMA_PID=$!
        sleep 3
        STARTED_OLLAMA=true
    else
        STARTED_OLLAMA=false
    fi

    ollama pull "$MODEL"

    if [ "$STARTED_OLLAMA" = true ] && [ -n "${OLLAMA_PID:-}" ]; then
        kill "$OLLAMA_PID" 2>/dev/null || true
    fi

    ok "Model '$MODEL' is ready"
}

# ── Step 5: Create data directory ─────────────────────────────────

setup_data() {
    step 5 "Preparing data directory..."
    mkdir -p "$SCRIPT_DIR/backend/data"
    ok "Data directory ready"
}

# ── Main ──────────────────────────────────────────────────────────

banner
check_python
setup_backend
install_ollama
pull_model
setup_data

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  ${BOLD}Installation complete!${NC}                                      ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  To start P.S.AI, run:"
echo ""
echo -e "    ${BOLD}bash launch.sh${NC}"
echo ""
echo -e "  Then open ${CYAN}http://localhost:8000/docs${NC} in your browser"
echo -e "  to see the API, or connect via the Flutter desktop app."
echo ""
