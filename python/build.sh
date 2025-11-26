#!/usr/bin/env bash
set -euo pipefail

# Build a wheel and sdist for the Python package
# Requires: python 3.9+ and the 'build' package (pip install build)

OUT_DIR="dist"
echo "Building wheel + sdist into ${OUT_DIR}/ from python/"
python3 -m build --outdir "${OUT_DIR}"

echo "Build finished. Artifacts:"
ls -la "${OUT_DIR}"
