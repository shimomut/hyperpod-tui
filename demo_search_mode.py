#!/usr/bin/env python3
"""Demo script showing the new incremental search mode functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.test_framework import KeySequenceSimulator, MockStdscr
from hyperpod_tui.main import HyperPodTUI


def demo_search_functionality():
    """Demonstrate the new search functionality."""
    print("=== HyperPod TUI - New Incremental Search Mode Demo ===\n")
    
    print("Key Changes:")
    print("1. Normal mode: Typing characters no longer immediately filters")
    print("2. Press 'f' to enter incremental search mode")
    print("3. In search mode: Type to filter, Up/Down to navigate")
    print("4. Press Enter to select, ESC to cancel search")
    print("5. Visual feedback shows current mode\n")
    
    # Demo sequence showing the new behavior
    demo_sequence = "j j f prod KEY_DOWN \n f test \x1b f cluster KEY_UP \n q"
    
    print("Demo sequence:")
    print("1. Navigate down twice (j j)")
    print("2. Press 'f' to start search, type 'prod'")
    print("3. Navigate with arrow keys, press Enter to select")
    print("4. Press 'f' again, type 'test', then ESC to cancel")
    print("5. Press 'f' once more, type 'cluster', navigate and select")
    print("6. Quit with 'q'\n")
    
    try:
        simulator = KeySequenceSimulator(demo_sequence)
        mock_stdscr = MockStdscr(simulator)
        
        tui = HyperPodTUI(mock_stdscr, test_mode=True)
        tui.run()
        
        print("Demo completed successfully!\n")
        
        # Show some key output lines
        output_lines = mock_stdscr.output_buffer
        search_lines = [line for line in output_lines if "Search:" in line or "(Press 'f' to search)" in line]
        
        if search_lines:
            print("Search mode indicators found in output:")
            for line in search_lines[-5:]:  # Show last 5 search-related lines
                print(f"  {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    demo_search_functionality()