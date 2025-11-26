#!/usr/bin/env bash
set -euo pipefail

# Build a wheel and sdist for the Python package
# Behavior (robust):
# 1. Prefer an existing venv at python/.venv
# 2. If none exists, try to create one using `python3 -m venv .venv`
# 3. Install build tools inside the venv and run the build
# This avoids attempting system-wide or user installs which may be blocked.

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR"

OUT_DIR="dist"
VENV_PY="$SCRIPT_DIR/.venv/bin/python"

echo "Building wheel + sdist into ${OUT_DIR}/ from ${SCRIPT_DIR}"

if [ -x "$VENV_PY" ]; then
	echo "Using existing virtualenv at ${SCRIPT_DIR}/.venv"
else
	echo "No virtualenv found at ${SCRIPT_DIR}/.venv — attempting to create one..."
	if python3 -m venv .venv 2>/dev/null; then
		echo "Virtualenv created at .venv"
	else
		cat <<'EOF'
ERROR: could not create a virtual environment automatically.
Most Linux distributions (Debian/Ubuntu) require the system package `python3-venv`.
Install it (sudo apt install python3-venv) and retry, or create a virtualenv manually and activate it.

Manual steps (recommended):
	python3 -m venv python/.venv
	source python/.venv/bin/activate
	python -m pip install --upgrade pip build wheel setuptools
	./build.sh
EOF
		exit 1
	fi
fi

VENV_PY="$SCRIPT_DIR/.venv/bin/python"

echo "Ensuring pip is available inside the venv..."
if ! $VENV_PY -m pip --version >/dev/null 2>&1; then
	echo "pip not found in venv — attempting to bootstrap pip with ensurepip..."
	if $VENV_PY -m ensurepip --upgrade >/dev/null 2>&1; then
		echo "ensurepip succeeded"
	else
		echo "ensurepip not available — attempting to install pip using get-pip.py (network required)"
		TMP_GET_PIP=$(mktemp)
		if command -v curl >/dev/null 2>&1; then
			curl -sS https://bootstrap.pypa.io/get-pip.py -o "$TMP_GET_PIP" || { echo 'Failed to download get-pip.py'; rm -f "$TMP_GET_PIP"; exit 1; }
		elif command -v wget >/dev/null 2>&1; then
			wget -q -O "$TMP_GET_PIP" https://bootstrap.pypa.io/get-pip.py || { echo 'Failed to download get-pip.py'; rm -f "$TMP_GET_PIP"; exit 1; }
		else
			echo "No curl/wget available to fetch get-pip.py; please install pip into the venv manually and re-run the script."
			exit 1
		fi

		$VENV_PY "$TMP_GET_PIP" || { echo 'Running get-pip.py failed'; rm -f "$TMP_GET_PIP"; exit 1; }
		rm -f "$TMP_GET_PIP"
	fi
fi

echo "Installing/ensuring build tools inside the venv..."
$VENV_PY -m pip install --upgrade pip setuptools wheel build

echo "Running build inside venv..."
$VENV_PY -m build --outdir "${OUT_DIR}"

echo "Build finished. Artifacts:"
ls -la "${OUT_DIR}"
