#!/usr/bin/env python3
"""Start the Fridge web server."""
import os, sys

# Ensure the package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fridge.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("fridge.main:app", host="0.0.0.0", port=8787, reload=True)
