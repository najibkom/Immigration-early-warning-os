#!/usr/bin/env bash
# Copy the Early-Warning OS template into a target folder without overwriting anything.
# Usage: setup.sh <target-folder>
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)/template"
DEST="${1:-$(pwd)}"
created=0; skipped=0
while IFS= read -r -d '' f; do
  rel="${f#"$SRC"/}"
  if [ -e "$DEST/$rel" ]; then
    skipped=$((skipped+1))
  else
    mkdir -p "$(dirname "$DEST/$rel")"
    cp "$f" "$DEST/$rel"
    created=$((created+1))
    echo "created  $rel"
  fi
done < <(find "$SRC" -type f -print0)
mkdir -p "$DEST/raw/_quarantine"
echo "---"
echo "created: $created  skipped (already there): $skipped"
