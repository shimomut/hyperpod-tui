#!/usr/bin/env python3
"""Interactive test for TAB key functionality."""

import curses
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.main import HyperPodTUI


def test_interactive(stdscr):
    """Interactive test function."""
    # Display instructions
    stdscr.clear()
    stdscr.addstr(0, 0, "TAB Key Interactive Test")
    stdscr.addstr(1, 0, "=" * 25)
    stdscr.addstr(3, 0, "Instructions:")
    stdscr.addstr(4, 0, "1. Press TAB to open JSON pane")
    stdscr.addstr(5, 0, "2. Press TAB again to switch focus")
    stdscr.addstr(6, 0, "3. Press TAB again to close JSON pane")
    stdscr.addstr(7, 0, "4. Press 'q' to quit")
    stdscr.addstr(9, 0, "Press any key to start the TUI...")
    stdscr.refresh()
    stdscr.getch()
    
    # Start the actual TUI
    tui = HyperPodTUI(stdscr)
    tui.run()


def main():
    """Main function."""
    print("TAB Key Interactive Test")
    print("========================")
    print("This will start the TUI where you can test the TAB key functionality.")
    print("Press Ctrl+C to exit if needed.")
    print()
    
    try:
        curses.wrapper(test_interactive)
        print("Test completed successfully!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()