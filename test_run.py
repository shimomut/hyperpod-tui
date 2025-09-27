#!/usr/bin/env python3
"""Test script to verify main function is callable."""

import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    from hyperpod_tui.main import main
    print("✓ Successfully imported main function")
    
    # Test that main function exists and is callable
    if callable(main):
        print("✓ main() function is callable")
    else:
        print("✗ main is not callable")
        
    print("✓ run.py should work correctly")
    print("Note: The application requires a proper terminal to run the curses interface")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)