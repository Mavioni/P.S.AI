#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR/backend"

# The pyproject.toml uses a non-standard build-backend
# (setuptools.backends._legacy:_Backend) that is not available in
# current setuptools. Work around by extracting and installing
# dependencies directly.
python3 - <<'PYEOF'
import tomllib, subprocess, sys, pathlib

pyproject = pathlib.Path("pyproject.toml")
cfg = tomllib.loads(pyproject.read_text())
proj = cfg["project"]

deps = list(proj.get("dependencies", []))
for extra in ("dev", "security"):
    deps.extend(proj.get("optional-dependencies", {}).get(extra, []))

subprocess.check_call(
    [sys.executable, "-m", "pip", "install"] + deps,
    stdout=subprocess.DEVNULL,
)
PYEOF

# Make the backend package importable (add to PYTHONPATH for the session)
echo "export PYTHONPATH=\"$CLAUDE_PROJECT_DIR/backend:\${PYTHONPATH:-}\"" >> "$CLAUDE_ENV_FILE"
