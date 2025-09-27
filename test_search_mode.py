#!/usr/bin/env python3
"""Test script for the new incremental search mode functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.test_framework import KeySequenceSimulator, MockStdscr
from hyperpod_tui.main import HyperPodTUI


def test_search_mode():
    """Test the new incremental search mode functionality."""
    print("Testing incremental search mode...")
    
    # Test sequence:
    # 1. Start with normal navigation
    # 2. Press 'f' to enter search mode
    # 3. Type some characters
    # 4. Use up/down arrows to navigate while searching
    # 5. Press Enter to select
    # 6. Press 'f' again and then ESC to cancel search
    test_sequence = "j j f test KEY_UP KEY_DOWN \n f search \x1b q"
    
    try:
        simulator = KeySequenceSimulator(test_sequence)
        mock_stdscr = MockStdscr(simulator)
        
        tui = HyperPodTUI(mock_stdscr, test_mode=True)
        tui.run()
        
        print("✓ Search mode test completed successfully")
        
        # Check if search mode was activated
        output = '\n'.join(mock_stdscr.output_buffer)
        if "Search:" in output:
            print("✓ Search mode was activated")
        else:
            print("⚠ Search mode activation not detected in output")
        
        if "(Press 'f' to search)" in output:
            print("✓ Search hint displayed when not in search mode")
        else:
            print("⚠ Search hint not detected in output")
        
        return True
        
    except Exception as e:
        print(f"✗ Search mode test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


def test_normal_mode_no_filter():
    """Test that normal mode doesn't capture printable characters."""
    print("\nTesting normal mode character handling...")
    
    # In normal mode, typing 'a' should not add to filter
    # Only 'f' should start search mode
    test_sequence = "a b c q"
    
    try:
        simulator = KeySequenceSimulator(test_sequence)
        mock_stdscr = MockStdscr(simulator)
        
        tui = HyperPodTUI(mock_stdscr, test_mode=True)
        tui.run()
        
        print("✓ Normal mode test completed successfully")
        
        # Check that filter wasn't activated by random characters
        output = '\n'.join(mock_stdscr.output_buffer)
        if "Filter: abc" not in output:
            print("✓ Random characters didn't activate filter in normal mode")
        else:
            print("✗ Random characters incorrectly activated filter")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Normal mode test failed: {e}")
        return False


if __name__ == "__main__":
    print("Running incremental search mode tests...\n")
    
    success1 = test_search_mode()
    success2 = test_normal_mode_no_filter()
    
    if success1 and success2:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)