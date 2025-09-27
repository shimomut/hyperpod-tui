#!/usr/bin/env python3
"""Test script for ESC key behavior in incremental search mode."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.tui import TUIScreen
from hyperpod_tui.config import config


class MockStdscr:
    """Mock curses stdscr for testing."""
    def __init__(self):
        self.height = 24
        self.width = 80
    
    def getmaxyx(self):
        return self.height, self.width
    
    def attron(self, attr):
        pass
    
    def attroff(self, attr):
        pass
    
    def addstr(self, y, x, text):
        pass
    
    def hline(self, y, x, char, width):
        pass
    
    def clear(self):
        pass
    
    def refresh(self):
        pass


def test_esc_behavior():
    """Test ESC key behavior in search mode."""
    print("Testing ESC key behavior in incremental search mode...")
    
    # Create a mock screen
    mock_stdscr = MockStdscr()
    screen = TUIScreen(mock_stdscr, "Test")
    
    # Test 1: ESC with empty filter text should exit search mode
    print("\nTest 1: ESC with empty filter text")
    screen.search_mode = True
    screen.filter_text = ""
    screen.caret_position = 0
    
    result = screen.handle_key('\x1b')  # ESC key
    print(f"  Filter text: '{screen.filter_text}'")
    print(f"  Search mode: {screen.search_mode}")
    print(f"  Result: {result}")
    
    expected_search_mode = False
    expected_result = 'search_cancelled'
    
    if screen.search_mode == expected_search_mode and result == expected_result:
        print("  ✓ PASS: ESC exits search mode when filter is empty")
    else:
        print(f"  ✗ FAIL: Expected search_mode={expected_search_mode}, result='{expected_result}'")
        print(f"         Got search_mode={screen.search_mode}, result='{result}'")
    
    # Test 2: ESC with non-empty filter text should clear filter first
    print("\nTest 2: ESC with non-empty filter text")
    screen.search_mode = True
    screen.filter_text = "test_filter"
    screen.caret_position = 5
    screen.selected_index = 2
    screen.scroll_offset = 1
    
    result = screen.handle_key('\x1b')  # ESC key
    print(f"  Filter text: '{screen.filter_text}'")
    print(f"  Search mode: {screen.search_mode}")
    print(f"  Caret position: {screen.caret_position}")
    print(f"  Selected index: {screen.selected_index}")
    print(f"  Scroll offset: {screen.scroll_offset}")
    print(f"  Result: {result}")
    
    expected_filter = ""
    expected_search_mode = True  # Should still be in search mode
    expected_caret = 0
    expected_selected = 0
    expected_scroll = 0
    expected_result = 'filter_changed'
    
    success = (screen.filter_text == expected_filter and 
               screen.search_mode == expected_search_mode and
               screen.caret_position == expected_caret and
               screen.selected_index == expected_selected and
               screen.scroll_offset == expected_scroll and
               result == expected_result)
    
    if success:
        print("  ✓ PASS: ESC clears filter when filter is not empty")
    else:
        print(f"  ✗ FAIL: Expected filter='', search_mode=True, caret=0, selected=0, scroll=0, result='filter_changed'")
    
    # Test 3: Second ESC after clearing filter should exit search mode
    print("\nTest 3: Second ESC after clearing filter")
    # screen should still be in search mode with empty filter from previous test
    
    result = screen.handle_key('\x1b')  # ESC key again
    print(f"  Filter text: '{screen.filter_text}'")
    print(f"  Search mode: {screen.search_mode}")
    print(f"  Result: {result}")
    
    expected_search_mode = False
    expected_result = 'search_cancelled'
    
    if screen.search_mode == expected_search_mode and result == expected_result:
        print("  ✓ PASS: Second ESC exits search mode")
    else:
        print(f"  ✗ FAIL: Expected search_mode=False, result='search_cancelled'")
        print(f"         Got search_mode={screen.search_mode}, result='{result}'")
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    test_esc_behavior()