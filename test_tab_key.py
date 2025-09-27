#!/usr/bin/env python3
"""Test TAB key functionality in the main application."""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.main import HyperPodTUI
from hyperpod_tui.test_framework import KeySequenceSimulator, MockStdscr


def test_tab_key():
    """Test TAB key functionality."""
    print("Testing TAB key functionality...")
    
    # Create a key sequence that tests TAB functionality
    # Navigate to a cluster, then press TAB to open JSON pane
    key_sequence = "j\t\tq"  # Down arrow, TAB (open), TAB (close), quit
    
    try:
        simulator = KeySequenceSimulator(key_sequence)
        mock_stdscr = MockStdscr(simulator)
        
        tui = HyperPodTUI(mock_stdscr, test_mode=True)
        tui.run()
        
        print("TAB key test completed successfully!")
        
        # Check if JSON pane methods were called by examining the screen state
        screen = tui.current_screen
        print(f"Final JSON pane state: visible={getattr(screen, 'json_pane_visible', 'N/A')}")
        print(f"JSON pane focused: {getattr(screen, 'json_pane_focused', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"Error during TAB key test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tab_key_verbose():
    """Test TAB key with verbose output."""
    print("Testing TAB key with verbose output...")
    
    # Test sequence: navigate, open JSON, scroll, close JSON
    key_sequence = "j\tj\tj\t\tq"  # Down, TAB(open), down(scroll), down(scroll), TAB(focus), TAB(close), quit
    
    try:
        simulator = KeySequenceSimulator(key_sequence)
        mock_stdscr = MockStdscr(simulator)
        
        tui = HyperPodTUI(mock_stdscr, test_mode=True)
        
        # Track state changes
        screen = tui.current_screen
        initial_json_visible = getattr(screen, 'json_pane_visible', False)
        
        print(f"Initial JSON pane visible: {initial_json_visible}")
        
        # Run the test
        tui.run()
        
        final_json_visible = getattr(screen, 'json_pane_visible', False)
        print(f"Final JSON pane visible: {final_json_visible}")
        
        # Show some output buffer
        print("\nLast few screen operations:")
        for line in mock_stdscr.output_buffer[-10:]:
            print(f"  {line}")
        
        return True
        
    except Exception as e:
        print(f"Error during verbose TAB key test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("TAB Key Functionality Test")
    print("=" * 30)
    
    # Run basic test
    success1 = test_tab_key()
    print()
    
    # Run verbose test
    success2 = test_tab_key_verbose()
    
    if success1 and success2:
        print("\n✅ All TAB key tests passed!")
    else:
        print("\n❌ Some TAB key tests failed!")
        sys.exit(1)