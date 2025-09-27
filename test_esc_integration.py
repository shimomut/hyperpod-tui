#!/usr/bin/env python3
"""Integration test for ESC key behavior in search mode."""

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


def test_esc_integration():
    """Test complete ESC behavior workflow."""
    print("Testing ESC key integration in search mode...")
    
    mock_stdscr = MockStdscr()
    screen = TUIScreen(mock_stdscr, "Test")
    
    # Test complete workflow
    print("\n=== Complete ESC Workflow Test ===")
    
    # 1. Start in normal mode
    print("1. Initial state:")
    print(f"   Search mode: {screen.search_mode}")
    print(f"   Filter text: '{screen.filter_text}'")
    assert not screen.search_mode, "Should start in normal mode"
    assert screen.filter_text == "", "Should start with empty filter"
    
    # 2. Enter search mode with 'f'
    result = screen.handle_key('f')
    print("2. After pressing 'f':")
    print(f"   Search mode: {screen.search_mode}")
    print(f"   Result: {result}")
    assert screen.search_mode, "Should be in search mode after 'f'"
    assert result == 'search_started', "Should return search_started"
    
    # 3. Type some filter text
    screen.handle_key('t')
    screen.handle_key('e')
    screen.handle_key('s')
    screen.handle_key('t')
    print("3. After typing 'test':")
    print(f"   Search mode: {screen.search_mode}")
    print(f"   Filter text: '{screen.filter_text}'")
    print(f"   Caret position: {screen.caret_position}")
    assert screen.search_mode, "Should still be in search mode"
    assert screen.filter_text == "test", "Should have 'test' as filter"
    assert screen.caret_position == 4, "Caret should be at end"
    
    # 4. First ESC - should clear filter but stay in search mode
    result = screen.handle_key('\x1b')
    print("4. After first ESC:")
    print(f"   Search mode: {screen.search_mode}")
    print(f"   Filter text: '{screen.filter_text}'")
    print(f"   Caret position: {screen.caret_position}")
    print(f"   Result: {result}")
    assert screen.search_mode, "Should still be in search mode"
    assert screen.filter_text == "", "Filter should be cleared"
    assert screen.caret_position == 0, "Caret should be reset"
    assert result == 'filter_changed', "Should return filter_changed"
    
    # 5. Second ESC - should exit search mode
    result = screen.handle_key('\x1b')
    print("5. After second ESC:")
    print(f"   Search mode: {screen.search_mode}")
    print(f"   Filter text: '{screen.filter_text}'")
    print(f"   Result: {result}")
    assert not screen.search_mode, "Should exit search mode"
    assert screen.filter_text == "", "Filter should remain empty"
    assert result == 'search_cancelled', "Should return search_cancelled"
    
    # 6. Test ESC with empty filter (should exit immediately)
    screen.handle_key('f')  # Enter search mode again
    result = screen.handle_key('\x1b')  # ESC with empty filter
    print("6. ESC with empty filter:")
    print(f"   Search mode: {screen.search_mode}")
    print(f"   Result: {result}")
    assert not screen.search_mode, "Should exit search mode immediately"
    assert result == 'search_cancelled', "Should return search_cancelled"
    
    print("\n✅ All integration tests passed!")
    return True


def test_edge_cases():
    """Test edge cases for ESC behavior."""
    print("\n=== Edge Cases Test ===")
    
    mock_stdscr = MockStdscr()
    screen = TUIScreen(mock_stdscr, "Test")
    
    # Test 1: Multiple ESC presses
    screen.handle_key('f')  # Enter search mode
    screen.handle_key('a')  # Add some text
    
    # Multiple ESC presses
    result1 = screen.handle_key('\x1b')  # Clear filter
    result2 = screen.handle_key('\x1b')  # Exit search
    result3 = screen.handle_key('\x1b')  # Should do nothing (not in search mode)
    
    print("Multiple ESC presses:")
    print(f"   First ESC result: {result1}")
    print(f"   Second ESC result: {result2}")
    print(f"   Third ESC result: {result3}")
    
    assert result1 == 'filter_changed', "First ESC should clear filter"
    assert result2 == 'search_cancelled', "Second ESC should exit search"
    assert result3 is None, "Third ESC should do nothing"
    
    # Test 2: ESC after caret movement
    screen.handle_key('f')  # Enter search mode
    screen.handle_key('h')
    screen.handle_key('e')
    screen.handle_key('l')
    screen.handle_key('l')
    screen.handle_key('o')  # "hello"
    
    # Move caret to middle
    screen.handle_key('KEY_LEFT')
    screen.handle_key('KEY_LEFT')  # Caret at position 3
    
    result = screen.handle_key('\x1b')  # ESC should clear and reset caret
    print("ESC after caret movement:")
    print(f"   Filter after ESC: '{screen.filter_text}'")
    print(f"   Caret after ESC: {screen.caret_position}")
    print(f"   Result: {result}")
    
    assert screen.filter_text == "", "Filter should be cleared"
    assert screen.caret_position == 0, "Caret should be reset to 0"
    assert result == 'filter_changed', "Should return filter_changed"
    
    print("✅ All edge case tests passed!")
    return True


if __name__ == "__main__":
    try:
        test_esc_integration()
        test_edge_cases()
        print("\n🎉 All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)