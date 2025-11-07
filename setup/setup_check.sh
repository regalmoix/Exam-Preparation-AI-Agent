#!/bin/bash
# Unix/Linux/macOS shell script wrapper for setup_check.py
# This makes it easier to run on Unix-like systems

set -e

echo "Running Setup Verification Script..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11+ from your package manager or https://www.python.org/downloads/"
    exit 1
fi

# Run the Python script from the setup directory
cd "$SCRIPT_DIR"
python3 setup_check.py

