#!/usr/bin/env bash
set -euo pipefail

PACKAGE_NAME="cascade-cms-rest"
MARKER_FILE="wiki/cascade-cms-wiki/docs/core-concepts/index.md"

# Look up the latest published version directly from PyPI's JSON API instead
# of importing cascade_cms — the library exposes no __version__ attribute,
# and its pyproject.toml version doesn't reliably track what's on PyPI.
CURRENT_VERSION=$(curl -sf "https://pypi.org/pypi/${PACKAGE_NAME}/json" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['info']['version'])")

if [[ -z "$CURRENT_VERSION" ]]; then
  echo "[detect_drift] ERROR: could not resolve latest version from PyPI" >&2
  exit 1
fi

# Extract version footer from last synthesized docs.
# Footer format: <!-- synthesized-for: 3.2.0 -->
if [[ -f "$MARKER_FILE" ]]; then
  DEPLOYED_VERSION=$(grep -oP '(?<=synthesized-for: )[\d.]+' "$MARKER_FILE" || echo "")
else
  DEPLOYED_VERSION=""
fi

echo "[detect_drift] Latest PyPI version:   $CURRENT_VERSION"
echo "[detect_drift] Deployed docs version: ${DEPLOYED_VERSION:-(none)}"

# Force override via workflow_dispatch input
FORCE="${FORCE_SYNTHESIS:-false}"

if [[ "$FORCE" == "true" ]]; then
  echo "[detect_drift] FORCE_SYNTHESIS=true — bypassing version check"
  HAS_DRIFT="true"
elif [[ "$CURRENT_VERSION" != "$DEPLOYED_VERSION" ]]; then
  echo "[detect_drift] Version mismatch — synthesis required"
  HAS_DRIFT="true"
else
  echo "[detect_drift] Versions match — skipping synthesis"
  HAS_DRIFT="false"
fi

{
  echo "has_drift=$HAS_DRIFT"
  echo "version=$CURRENT_VERSION"
} >> "$GITHUB_OUTPUT"
