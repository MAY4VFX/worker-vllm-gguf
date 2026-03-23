#!/bin/bash
# Download model files before starting handler
python3 /src/download_model.py
# Start the handler
exec python3 /src/handler.py
