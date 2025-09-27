#!/usr/bin/env python3
"""Test script to verify backspace key functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.test_framework import KeySequenceSimulator, MockStdscr
from hyperpod_tui.tui import ClusterListScreen
from hyperpod_tui.aws_client import HyperPodClient


def test_backspace_in_search_mode():
    """Test backspace functionality in search mode."""
    print("Testing backspace in search mode...")
    
    # Test different backspace key representations
    backspace_keys = ['KEY_BACKSPACE', '\b', '\x7f', '\x08']
    
    for backspace_key in backspace_keys:
        print(f"  Testing backspace key: {repr(backspace_key)}")
        
        # Create key sequence: enter search mode, type text, then backspace
        key_sequence = f"f test{backspace_key} q"
        simulator = KeySequenceSimulator(key_sequence)
        mock_stdscr = MockStdscr(simulator)
        
        # Create screen and client
        client = HyperPodClient()
        screen = ClusterListScreen(mock_stdscr, client)
        
        # Simulate the key sequence
        try:
            # Enter search mode
            action = screen.handle_key('f')
            assert action == 'search_started', f"Failed to start search mode"
            assert screen.search_mode == True, f"Search mode not activated"
            
            # Type some text
            for char in 'test':
                action = screen.handle_key(char)
                assert action == 'filter_changed', f"Failed to add character {char}"
            
            assert screen.filter_text == 'test', f"Filter text should be 'test', got '{screen.filter_text}'"
            
            # Test backspace
            action = screen.handle_key(backspace_key)
            if screen.filter_text:  # Only if there's text to delete
                assert action == 'filter_changed', f"Backspace should return 'filter_changed' for key {repr(backspace_key)}"
                assert screen.filter_text == 'tes', f"Filter text should be 'tes' after backspace, got '{screen.filter_text}'"
            
            print(f"    ✓ Backspace key {repr(backspace_key)} works correctly")
            
        except Exception as e:
            print(f"    ✗ Backspace key {repr(backspace_key)} failed: {e}")
            return False
    
    return True


def test_backspace_for_navigation():
    """Test backspace functionality for going back/up a level."""
    print("Testing backspace for navigation...")
    
    backspace_keys = ['KEY_BACKSPACE', '\b', '\x7f', '\x08']
    
    for backspace_key in backspace_keys:
        print(f"  Testing navigation backspace key: {repr(backspace_key)}")
        
        simulator = KeySequenceSimulator(backspace_key)
        mock_stdscr = MockStdscr(simulator)
        
        client = HyperPodClient()
        screen = ClusterListScreen(mock_stdscr, client)
        
        try:
            # Test backspace in normal mode (should return 'back')
            action = screen.handle_key(backspace_key)
            assert action == 'back', f"Backspace in normal mode should return 'back', got '{action}'"
            
            print(f"    ✓ Navigation backspace key {repr(backspace_key)} works correctly")
            
        except Exception as e:
            print(f"    ✗ Navigation backspace key {repr(backspace_key)} failed: {e}")
            return False
    
    return True


def test_backspace_edge_cases():
    """Test edge cases for backspace functionality."""
    print("Testing backspace edge cases...")
    
    simulator = KeySequenceSimulator('KEY_BACKSPACE')
    mock_stdscr = MockStdscr(simulator)
    
    client = HyperPodClient()
    screen = ClusterListScreen(mock_stdscr, client)
    
    try:
        # Test backspace in search mode with empty filter
        screen.search_mode = True
        screen.filter_text = ""
        
        action = screen.handle_key('KEY_BACKSPACE')
        # Should not crash and should not change anything
        assert screen.filter_text == "", "Empty filter should remain empty after backspace"
        assert action is None or action == 'filter_changed', "Backspace on empty filter should return None or filter_changed"
        
        print("    ✓ Backspace on empty filter works correctly")
        
        # Test backspace with single character
        screen.filter_text = "a"
        action = screen.handle_key('KEY_BACKSPACE')
        assert action == 'filter_changed', "Backspace should return 'filter_changed'"
        assert screen.filter_text == "", "Single character should be removed"
        
        print("    ✓ Backspace with single character works correctly")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Edge case test failed: {e}")
        return False


def main():
    """Run all backspace tests."""
    print("Running backspace functionality tests...\n")
    
    tests = [
        test_backspace_in_search_mode,
        test_backspace_for_navigation,
        test_backspace_edge_cases,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✓ PASSED\n")
            else:
                print("✗ FAILED\n")
        except Exception as e:
            print(f"✗ ERROR: {e}\n")
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backspace tests passed!")
        return True
    else:
        print("❌ Some backspace tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)