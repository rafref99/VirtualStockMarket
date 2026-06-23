#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "Starting Virtual Stock Market..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required but was not found."
  echo "Install Python 3 from https://www.python.org/downloads/ and run this again."
  read -r -p "Press Enter to close..."
  exit 1
fi

PYTHON_VERSION="$(python3 - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"
echo "Found Python $PYTHON_VERSION"

python3 - <<'PY'
try:
    import tkinter
except Exception as exc:
    raise SystemExit(
        "Tkinter is required for the desktop app but is not available in this Python installation.\n"
        "Install a Python build that includes Tkinter, then run this launcher again."
    ) from exc
PY

if [ -f "requirements.txt" ] && grep -Eq '^[[:space:]]*[^#[:space:]]' requirements.txt; then
  echo "Checking and installing Python package requirements..."
  python3 -m pip install --upgrade pip
  python3 -m pip install -r requirements.txt
else
  echo "No third-party packages are listed in requirements.txt."
fi

echo "Launching app..."
python3 app.py

echo "App closed."
read -r -p "Press Enter to close..."
