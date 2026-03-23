#!/bin/bash
# Ensure gguf package is installed (fixes "Invalid version: 'N/A'" from transformers)
pip install -q gguf 2>/dev/null

# Download model files before starting handler
python3 /src/download_model.py

# Start the handler
exec python3 /src/handler.py
