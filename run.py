#!/usr/bin/env python3
"""Simple script to run HyperPod TUI."""

import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def check_terminal():
    """Check if we're running in a proper terminal."""
    if not sys.stdout.isatty():
        print("Error: HyperPod TUI requires a proper terminal environment.")
        print("Please run this from a terminal/command prompt, not from an IDE or script.")
        return False
    return True

if __name__ == "__main__":
    # Check if we're running tests or in test mode
    test_mode = any(arg in sys.argv for arg in ['--test-key-seq', '--test-scenario', '--list-tests', '--run-all-tests'])
    
    if not test_mode and not check_terminal():
        sys.exit(1)
        
    try:
        from hyperpod_tui.main import main
        
        if not test_mode:
            print("Starting HyperPod TUI...")
            print("Press 'q' to quit once the interface loads.")
        
        main()
    except KeyboardInterrupt:
        if not test_mode:
            print("\nExiting...")
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)