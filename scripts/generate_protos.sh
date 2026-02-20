#!/usr/bin/env bash
# P.S.AI — Protobuf Compilation Script
#
# Compiles psai.proto into Python and Dart stubs.
# Usage: ./scripts/generate_protos.sh

set -euo pipefail

PROTO_DIR="protos"
PROTO_FILE="${PROTO_DIR}/psai.proto"

echo "Compiling P.S.AI protobuf schema..."

# Python stubs
PYTHON_OUT="backend/app/generated"
mkdir -p "${PYTHON_OUT}"

if command -v protoc &> /dev/null; then
    protoc \
        --proto_path="${PROTO_DIR}" \
        --python_out="${PYTHON_OUT}" \
        --pyi_out="${PYTHON_OUT}" \
        "${PROTO_FILE}"
    echo "  ✓ Python stubs generated in ${PYTHON_OUT}"
else
    echo "  ⚠ protoc not found — install Protocol Buffers compiler"
    echo "    brew install protobuf  (macOS)"
    echo "    apt install protobuf-compiler  (Linux)"
fi

# Dart stubs
DART_OUT="frontend/lib/generated"
mkdir -p "${DART_OUT}"

if command -v protoc-gen-dart &> /dev/null; then
    protoc \
        --proto_path="${PROTO_DIR}" \
        --dart_out="${DART_OUT}" \
        "${PROTO_FILE}"
    echo "  ✓ Dart stubs generated in ${DART_OUT}"
else
    echo "  ⚠ protoc-gen-dart not found — install with:"
    echo "    dart pub global activate protoc_plugin"
fi

echo ""
echo "Proto compilation complete."
