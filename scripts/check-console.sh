#!/bin/bash
# Console error check: run Playwright test for console errors
set -e

echo "Running console error check..."
cd e2e && npx playwright test console-check.spec.ts 2>&1 || {
  echo "FAIL: Console errors detected on key pages"
  exit 1
}

echo "Console error check complete. No errors detected."