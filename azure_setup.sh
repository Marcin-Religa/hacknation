#!/bin/bash
set -e

echo ">>> Updating system packages..."
sudo apt-get update && sudo apt-get install -y python3-venv python3-pip git

echo ">>> Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo ">>> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> Setup complete. Activate with: source .venv/bin/activate"
