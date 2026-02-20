#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  P.S.AI — Launcher                                              ║
# ║  Starts Ollama + backend. Run install.sh first.                  ║
# ║  Usage: bash launch.sh                                           ║
# ║  Stop:  Press Ctrl+C                                             ║
# ╚══════════════════════════════════════════════════════════════════╝

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

VENV_DIR="$SCRIPT_DIR/.venv"
PORT="${PSAI_PORT:-8000}"
OLLAMA_PID=""
BACKEND_PID=""

# ── Cleanup on exit ───────────────────────────────────────────────

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down P.S.AI...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
        echo -e "  ${GREEN}✓${NC} Backend stopped"
    fi
    if [ -n "$OLLAMA_PID" ]; then
        kill "$OLLAMA_PID" 2>/dev/null || true
        wait "$OLLAMA_PID" 2>/dev/null || true
        echo -e "  ${GREEN}✓${NC} Ollama stopped"
    fi
    echo -e "${GREEN}Goodbye.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# ── Preflight checks ─────────────────────────────────────────────

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Error:${NC} Virtual environment not found."
    echo "  Please run ${BOLD}bash install.sh${NC} first."
    exit 1
fi

if ! command -v ollama &>/dev/null; then
    echo -e "${RED}Error:${NC} Ollama is not installed."
    echo "  Please run ${BOLD}bash install.sh${NC} first."
    exit 1
fi

# ── Start Ollama ──────────────────────────────────────────────────

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  ${BOLD}P.S.AI — Starting...${NC}                                       ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

if curl -sf http://localhost:11434/api/tags &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Ollama is already running"
else
    echo -e "  ${YELLOW}→${NC} Starting Ollama..."
    ollama serve &>/dev/null &
    OLLAMA_PID=$!

    # Wait for Ollama to be ready
    for i in $(seq 1 30); do
        if curl -sf http://localhost:11434/api/tags &>/dev/null; then
            break
        fi
        sleep 1
    done

    if curl -sf http://localhost:11434/api/tags &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Ollama started"
    else
        echo -e "  ${RED}✗${NC} Ollama failed to start. Check 'ollama serve' manually."
        exit 1
    fi
fi

# ── Start backend ────────────────────────────────────────────────

echo -e "  ${YELLOW}→${NC} Starting P.S.AI backend on port $PORT..."

source "$VENV_DIR/bin/activate"

export PSAI_ONTOLOGY_PATH="$SCRIPT_DIR/ontology"
export PSAI_DB_PATH="$SCRIPT_DIR/backend/data/psai.db"
export OLLAMA_BASE_URL="http://localhost:11434"

cd "$SCRIPT_DIR/backend"
uvicorn app.main:app --host 127.0.0.1 --port "$PORT" &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for backend to be ready
for i in $(seq 1 20); do
    if curl -sf "http://localhost:$PORT/api/health" &>/dev/null; then
        break
    fi
    sleep 1
done

if curl -sf "http://localhost:$PORT/api/health" &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Backend is running"
else
    echo -e "  ${YELLOW}!${NC} Backend is starting (may still be loading personas)..."
fi

# ── Open browser ─────────────────────────────────────────────────

URL="http://localhost:$PORT/docs"
echo ""
echo -e "  ${GREEN}P.S.AI is running!${NC}"
echo ""
echo -e "  API docs:    ${CYAN}$URL${NC}"
echo -e "  Health:      ${CYAN}http://localhost:$PORT/api/health${NC}"
echo -e "  Personas:    ${CYAN}http://localhost:$PORT/api/personas${NC}"
echo ""

# Try to open browser
if command -v xdg-open &>/dev/null; then
    xdg-open "$URL" 2>/dev/null || true
elif command -v open &>/dev/null; then
    open "$URL" 2>/dev/null || true
fi

echo -e "  Press ${BOLD}Ctrl+C${NC} to stop."
echo ""

# ── Wait ─────────────────────────────────────────────────────────

wait "$BACKEND_PID"
