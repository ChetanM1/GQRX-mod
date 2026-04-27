#!/usr/bin/env bash
set -euo pipefail

# Install Python dependencies used by optional backend scripts (capture.py/plotting.py).
# Usage:
#   ./tools/install_python_backend_deps.sh [--upgrade]

UPGRADE=0
if [[ "${1:-}" == "--upgrade" ]]; then
  UPGRADE=1
elif [[ $# -gt 0 ]]; then
  echo "Unknown argument: $1" >&2
  echo "Usage: $0 [--upgrade]" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found in PATH." >&2
  exit 1
fi

if ! python3 -m pip --version >/dev/null 2>&1; then
  echo "pip for python3 is required but not available." >&2
  echo "Install it with your package manager (example: sudo apt-get install python3-pip)." >&2
  exit 1
fi

REQS=(
  numpy
  scipy
  matplotlib
  sigmf
)

PIP_ARGS=(install --user)
if [[ $UPGRADE -eq 1 ]]; then
  PIP_ARGS+=(--upgrade)
fi

echo "Installing Python backend dependencies: ${REQS[*]}"
python3 -m pip "${PIP_ARGS[@]}" "${REQS[@]}"

echo "Done. You can now retry 'Process SigMF/Raw Data' in Gqrx."
