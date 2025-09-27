#!/usr/bin/env python3
"""Demo script showing HyperPod TUI automated testing capabilities."""

import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)


def demo_basic_testing():
    """Demonstrate basic testing functionality."""
    print("=" * 60)
    print("HyperPod TUI Automated Testing Demo")
    print("=" * 60)
    print()
    
    print("This demo shows how to test the TUI application automatically")
    print("without manual keyboard input.")
    print()
    
    # Demo 1: Simple key sequence
    print("Demo 1: Simple key sequence test")
    print("Key sequence: 'q' (immediate quit)")
    print("Command: python run.py --test-key-seq 'q'")
    print()
    
    # Demo 2: Navigation test
    print("Demo 2: Navigation test")
    print("Key sequence: '<DOWN><DOWN><UP><ENTER>q'")
    print("- Navigate down twice")
    print("- Navigate up once")
    print("- Press Enter")
    print("- Quit")
    print("Command: python run.py --test-key-seq '<DOWN><DOWN><UP><ENTER>q'")
    print()
    
    # Demo 3: Filter test
    print("Demo 3: Filter test")
    print("Key sequence: 'test<DELETE>prod<BACKSPACE><BACKSPACE><BACKSPACE><BACKSPACE>q'")
    print("- Type 'test' filter")
    print("- Clear with DELETE")
    print("- Type 'prod' filter")
    print("- Clear with backspace")
    print("- Quit")
    print("Command: python run.py --test-key-seq 'test<DELETE>prod<BACKSPACE><BACKSPACE><BACKSPACE><BACKSPACE>q'")
    print()
    
    # Demo 4: Predefined scenarios
    print("Demo 4: Predefined test scenarios")
    print("Available scenarios:")
    
    try:
        from hyperpod_tui.test_scenarios import get_all_test_scenarios
        for scenario in get_all_test_scenarios():
            print(f"  - {scenario.name}: {scenario.description}")
    except ImportError:
        print("  (Import error - run from project root)")
    
    print()
    print("Run a scenario: python run.py --test-scenario basic_navigation")
    print("List all scenarios: python run.py --list-tests")
    print("Run all scenarios: python run.py --run-all-tests")
    print()
    
    # Demo 5: Test runner
    print("Demo 5: Dedicated test runner")
    print("Commands:")
    print("  python test_tui.py --list                    # List tests")
    print("  python test_tui.py --all                     # Run all tests")
    print("  python test_tui.py --all --quick             # Run quick tests")
    print("  python test_tui.py --scenario basic_navigation  # Run specific test")
    print("  python test_tui.py --key-seq '<DOWN>q'       # Custom key sequence")
    print("  python test_tui.py --all --verbose           # Verbose output")
    print()
    
    print("=" * 60)
    print("Try running these commands to see the testing system in action!")
    print("=" * 60)


def run_sample_test():
    """Run a sample test to demonstrate the system."""
    print("Running sample test...")
    print()
    
    try:
        from hyperpod_tui.test_framework import KeySequenceSimulator, MockStdscr
        from hyperpod_tui.main import HyperPodTUI
        
        # Simple test: start app and quit immediately
        key_sequence = "q"
        print(f"Key sequence: '{key_sequence}'")
        print("Expected behavior: Start app and quit immediately")
        print()
        
        simulator = KeySequenceSimulator(key_sequence)
        mock_stdscr = MockStdscr(simulator)
        
        tui = HyperPodTUI(mock_stdscr, test_mode=True)
        tui.run()
        
        print("✓ Test completed successfully!")
        print()
        print("Screen output (last 10 lines):")
        for line in mock_stdscr.output_buffer[-10:]:
            print(f"  {line}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the project root directory")
    except Exception as e:
        print(f"Error running test: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run-sample":
        run_sample_test()
    else:
        demo_basic_testing()