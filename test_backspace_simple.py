#!/usr/bin/env python3
"""Simple test to verify backspace key handling works correctly."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.test_framework import KeySequenceSimulator, MockStdscr
from hyperpod_tui.tui import TUIScreen


class TestScreen(TUIScreen):
    """Simple test screen for testing key handling."""
    
    def __init__(self, stdscr):
        super().__init__(stdscr, "Test")
        self.items = ["item1", "item2", "item3"]
    
    def draw(self):
        """Simple draw method."""
        self.stdscr.clear()
        self.draw_header()
        self.draw_filter()
        self.draw_footer()
        self.stdscr.refresh()
    
    def get_filtered_items(self, items):
        """Override to use test items."""
        return [item for item in self.items if self.filter_text.lower() in item.lower()]


def test_backspace_functionality():
    """Test backspace functionality comprehensively."""
    print("Testing backspace functionality...")
    
    # Test different backspace representations
    backspace_variants = [
        ('KEY_BACKSPACE', 'Standard curses backspace'),
        ('\b', 'ASCII backspace (Ctrl+H)'),
        ('\x7f', 'DEL character'),
        ('\x08', 'Another backspace representation'),
    ]
    
    for backspace_key, description in backspace_variants:
        print(f"\n  Testing {description}: {repr(backspace_key)}")
        
        # Create mock screen
        simulator = KeySequenceSimulator("")
        mock_stdscr = MockStdscr(simulator)
        screen = TestScreen(mock_stdscr)
        
        # Test 1: Backspace in search mode with text
        print("    Test 1: Backspace in search mode with text")
        screen.search_mode = True
        screen.filter_text = "test"
        
        action = screen.handle_key(backspace_key)
        if action == 'filter_changed' and screen.filter_text == "tes":
            print("      ✓ Successfully removed character from filter")
        else:
            print(f"      ✗ Failed - action: {action}, filter: '{screen.filter_text}'")
            return False
        
        # Test 2: Backspace in search mode with empty text
        print("    Test 2: Backspace in search mode with empty text")
        screen.filter_text = ""
        action = screen.handle_key(backspace_key)
        if screen.filter_text == "":
            print("      ✓ Empty filter remains empty")
        else:
            print(f"      ✗ Failed - filter should be empty, got: '{screen.filter_text}'")
            return False
        
        # Test 3: Backspace in normal mode (navigation)
        print("    Test 3: Backspace in normal mode (navigation)")
        screen.search_mode = False
        action = screen.handle_key(backspace_key)
        if action == 'back':
            print("      ✓ Returns 'back' action for navigation")
        else:
            print(f"      ✗ Failed - should return 'back', got: '{action}'")
            return False
    
    return True


def test_search_mode_workflow():
    """Test complete search mode workflow with backspace."""
    print("\nTesting complete search mode workflow...")
    
    simulator = KeySequenceSimulator("")
    mock_stdscr = MockStdscr(simulator)
    screen = TestScreen(mock_stdscr)
    
    # Start search mode
    action = screen.handle_key('f')
    if action != 'search_started' or not screen.search_mode:
        print("  ✗ Failed to start search mode")
        return False
    print("  ✓ Search mode started")
    
    # Type some text
    for char in "hello":
        action = screen.handle_key(char)
        if action != 'filter_changed':
            print(f"  ✗ Failed to add character '{char}'")
            return False
    
    if screen.filter_text != "hello":
        print(f"  ✗ Filter text should be 'hello', got '{screen.filter_text}'")
        return False
    print("  ✓ Text typed successfully")
    
    # Use backspace to delete characters
    for expected in ["hell", "hel", "he", "h", ""]:
        action = screen.handle_key('KEY_BACKSPACE')
        if expected == "":
            # Last backspace on empty string
            if screen.filter_text != "":
                print(f"  ✗ Filter should be empty, got '{screen.filter_text}'")
                return False
        else:
            if action != 'filter_changed' or screen.filter_text != expected:
                print(f"  ✗ Expected '{expected}', got '{screen.filter_text}'")
                return False
    
    print("  ✓ Backspace sequence worked correctly")
    
    # Exit search mode
    action = screen.handle_key('\x1b')  # ESC
    if action != 'search_cancelled' or screen.search_mode:
        print("  ✗ Failed to exit search mode")
        return False
    print("  ✓ Search mode exited successfully")
    
    return True


def main():
    """Run all tests."""
    print("Running backspace functionality tests...\n")
    
    tests = [
        test_backspace_functionality,
        test_search_mode_workflow,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✓ PASSED")
            else:
                print("✗ FAILED")
        except Exception as e:
            print(f"✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backspace tests passed!")
        print("\nBackspace key should now work correctly in both:")
        print("- Search mode (deleting characters)")
        print("- Navigation mode (going back/up)")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)