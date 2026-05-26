#!/bin/bash
# Mobile page check: capture screenshots at 375px viewport width
set -e

PAGES=("/" "/notices" "/talk-record" "/students" "/risks")
BASE_URL="http://localhost:5173"
SCREENSHOT_DIR="e2e/screenshots"

mkdir -p "$SCREENSHOT_DIR"

for path in "${PAGES[@]}"; do
  filename="mobile-${path//\//_}.png"
  if [ "$path" = "/" ]; then
    filename="mobile-root.png"
  fi
  echo "Checking mobile viewport: $path → $SCREENSHOT_DIR/$filename"
  npx playwright screenshot --viewport-size="375,812" "$BASE_URL$path" "$SCREENSHOT_DIR/$filename" 2>&1 || {
    echo "WARNING: Could not capture screenshot for $path (server may not be running)"
  }
done

echo "Mobile page check complete. Screenshots saved to $SCREENSHOT_DIR/"