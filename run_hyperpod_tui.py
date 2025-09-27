#!/usr/bin/env python3
"""
Simple runner script for HyperPod TUI.
This script handles the Python path setup and runs the application.
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
from hyperpod_tui.main import main

if __name__ == "__main__":
    main()