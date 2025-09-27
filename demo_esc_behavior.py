#!/usr/bin/env python3
"""Demo script showing the new ESC key behavior in search mode."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.tui import TUIScreen


class MockStdscr:
    """Mock curses stdscr for demo."""
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


def demo_esc_behavior():
    """Demonstrate the new ESC key behavior."""
    print("🔍 HyperPod TUI - ESC Key Behavior Demo")
    print("=" * 50)
    
    mock_stdscr = MockStdscr()
    screen = TUIScreen(mock_stdscr, "Demo")
    
    def show_state():
        mode = "🔍 SEARCH" if screen.search_mode else "📋 NORMAL"
        filter_display = f"'{screen.filter_text}'" if screen.filter_text else "(empty)"
        print(f"   Mode: {mode}")
        print(f"   Filter: {filter_display}")
        print(f"   Caret: {screen.caret_position}")
    
    print("\n1️⃣  Starting in normal mode:")
    show_state()
    
    print("\n2️⃣  Press 'f' to enter search mode:")
    screen.handle_key('f')
    show_state()
    
    print("\n3️⃣  Type 'production' to filter:")
    for char in "production":
        screen.handle_key(char)
    show_state()
    
    print("\n4️⃣  Press ESC once (clears filter, stays in search mode):")
    result = screen.handle_key('\x1b')
    print(f"   Action result: {result}")
    show_state()
    
    print("\n5️⃣  Press ESC again (exits search mode):")
    result = screen.handle_key('\x1b')
    print(f"   Action result: {result}")
    show_state()
    
    print("\n6️⃣  Enter search mode and press ESC immediately (exits directly):")
    screen.handle_key('f')
    print("   After entering search mode:")
    show_state()
    result = screen.handle_key('\x1b')
    print(f"   After ESC with empty filter:")
    print(f"   Action result: {result}")
    show_state()
    
    print("\n7️⃣  Practical workflow - correct a typo:")
    screen.handle_key('f')  # Enter search
    for char in "prodction":  # Typo: missing 'u'
        screen.handle_key(char)
    print("   Typed 'prodction' (typo):")
    show_state()
    
    screen.handle_key('\x1b')  # Clear filter
    print("   After ESC (cleared typo, still in search mode):")
    show_state()
    
    for char in "production":  # Correct spelling
        screen.handle_key(char)
    print("   Typed 'production' (corrected):")
    show_state()
    
    screen.handle_key('\n')  # Enter to select
    print("   After Enter (selected and exited search mode):")
    show_state()
    
    print("\n✨ Demo completed!")
    print("\n📝 Summary of ESC behavior:")
    print("   • ESC with filter text → Clears filter, stays in search mode")
    print("   • ESC with empty filter → Exits search mode")
    print("   • This allows easy correction without mode switching")
    print("   • More forgiving workflow for users")


if __name__ == "__main__":
    demo_esc_behavior()