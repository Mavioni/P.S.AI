#!/usr/bin/env bash
# P.S.AI — Model Setup Script
#
# Downloads and verifies LLM models for local inference via Ollama.
# Usage: ./scripts/setup_models.sh [model_name]

set -euo pipefail

MODEL="${1:-llama3}"
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"

echo "╔══════════════════════════════════════════════╗"
echo "║        P.S.AI — Model Setup                  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check Ollama is running
echo "[1/3] Checking Ollama availability..."
if ! curl -sf "${OLLAMA_HOST}/api/tags" > /dev/null 2>&1; then
    echo "ERROR: Ollama is not reachable at ${OLLAMA_HOST}"
    echo "Start Ollama first: ollama serve"
    exit 1
fi
echo "  ✓ Ollama is running at ${OLLAMA_HOST}"

# Pull model
echo ""
echo "[2/3] Pulling model: ${MODEL}..."
ollama pull "${MODEL}"
echo "  ✓ Model ${MODEL} is ready"

# Verify
echo ""
echo "[3/3] Verifying model..."
RESPONSE=$(curl -sf "${OLLAMA_HOST}/api/tags" | python3 -c "
import sys, json
data = json.load(sys.stdin)
models = [m['name'] for m in data.get('models', [])]
if '${MODEL}' in models or any('${MODEL}' in m for m in models):
    print('VERIFIED')
else:
    print('NOT_FOUND')
")

if [ "${RESPONSE}" = "VERIFIED" ]; then
    echo "  ✓ Model ${MODEL} verified and ready for P.S.AI"
else
    echo "  ✗ Model verification failed"
    exit 1
fi

echo ""
echo "Setup complete. Start P.S.AI with:"
echo "  cd backend && uvicorn app.main:app --reload"
