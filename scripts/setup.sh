#!/usr/bin/env bash
# One-step setup for the Wearable Assistant Context Benchmark.
# Creates a venv, installs pinned dependencies, and downloads the
# spaCy model used by the validator and the scoring code path.
#
# Usage: ./scripts/setup.sh
# Override the Python interpreter with PYTHON=python3.13 ./scripts/setup.sh
set -euo pipefail

PY="${PYTHON:-python3}"

if [ ! -d ".venv" ]; then
  "$PY" -m venv .venv
fi

# shellcheck disable=SC1091
. .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm

echo
echo "Setup complete. Activate the venv with:"
echo "    source .venv/bin/activate"
echo
echo "Verify the install:"
echo "    python -m pytest tests/ -q"
echo "    python scripts/validate_scenarios.py"
