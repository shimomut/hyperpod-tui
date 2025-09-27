#!/usr/bin/env python3
"""Demo script showing JSON pane functionality with sample data."""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.main import HyperPodTUI
from hyperpod_tui.test_framework import KeySequenceSimulator, MockStdscr


def demo_json_pane():
    """Demonstrate JSON pane functionality."""
    print("JSON Pane Demo")
    print("==============")
    print("This demo shows the JSON pane functionality with a sequence of actions:")
    print("1. Navigate down to select a cluster")
    print("2. Press TAB to open JSON pane")
    print("3. Navigate in the JSON pane")
    print("4. Press TAB to switch focus back to main panes")
    print("5. Press TAB again to close JSON pane")
    print("6. Quit")
    print()
    
    # Create a comprehensive key sequence
    key_sequence = (
        "j"      # Navigate down to select second cluster
        "j"      # Navigate down again
        "\t"     # Open JSON pane (should focus JSON pane)
        "j"      # Scroll down in JSON pane
        "j"      # Scroll down more in JSON pane
        "j"      # Scroll down more in JSON pane
        "\t"     # Switch focus back to main panes
        "k"      # Navigate up in main panes (should work now)
        "\t"     # Focus JSON pane again
        "k"      # Scroll up in JSON pane
        "\t"     # Switch focus back to main panes
        "\t"     # Close JSON pane (since main panes are focused)
        "q"      # Quit
    )
    
    try:
        simulator = KeySequenceSimulator(key_sequence)
        mock_stdscr = MockStdscr(simulator)
        
        print("Running demo...")
        tui = HyperPodTUI(mock_stdscr, test_mode=True)
        tui.run()
        
        print("Demo completed successfully!")
        
        # Show final state
        screen = tui.current_screen
        print(f"\nFinal state:")
        print(f"  JSON pane visible: {getattr(screen, 'json_pane_visible', 'N/A')}")
        print(f"  JSON pane focused: {getattr(screen, 'json_pane_focused', 'N/A')}")
        print(f"  Selected index: {getattr(screen, 'selected_index', 'N/A')}")
        
        # Show some key operations from the output buffer
        print(f"\nKey operations performed:")
        json_operations = [line for line in mock_stdscr.output_buffer if 'JSON' in line]
        for op in json_operations[-10:]:  # Show last 10 JSON-related operations
            print(f"  {op}")
        
        return True
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = demo_json_pane()
    if success:
        print("\n✅ JSON pane demo completed successfully!")
    else:
        print("\n❌ JSON pane demo failed!")
        sys.exit(1)