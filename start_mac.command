#!/bin/bash
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install it from https://www.python.org/downloads/macos/"
  read -r -p "Press Return to close..."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating the project environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate

if [ ! -x ".venv/bin/streamlit" ]; then
  echo "Installing project dependencies (first run only)..."
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

echo "Starting IoT Sentinel..."
python -m streamlit run main.py
