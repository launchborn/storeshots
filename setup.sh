#!/usr/bin/env bash
# Create a local virtualenv and install dependencies for storeshots.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d venv ]; then
  echo "Creating virtualenv in ./venv ..."
  python3 -m venv venv
fi

echo "Installing dependencies ..."
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q -r requirements.txt

echo
echo "Done. Run the tool with:"
echo "  ./venv/bin/python3 compose.py --config path/to/config.json"
