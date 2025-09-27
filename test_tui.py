#!/usr/bin/env python3
"""Test runner for HyperPod TUI automated testing."""

import sys
import os
import argparse

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="HyperPod TUI Test Runner")
    parser.add_argument("--scenario", "-s", type=str, help="Run a specific test scenario")
    parser.add_argument("--key-seq", "-k", type=str, help="Run with custom key sequence")
    parser.add_argument("--list", "-l", action="store_true", help="List available test scenarios")
    parser.add_argument("--all", "-a", action="store_true", help="Run all test scenarios")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quick", "-q", action="store_true", help="Run quick tests only")
    
    args = parser.parse_args()
    
    try:
        if args.list:
            from hyperpod_tui.test_scenarios import list_available_tests
            list_available_tests()
            return
        
        if args.all:
            from hyperpod_tui.test_scenarios import create_test_runner
            runner = create_test_runner(verbose=args.verbose)
            
            if args.quick:
                # Filter to quick tests only
                quick_tests = ['quick_exit', 'basic_navigation', 'filter_functionality']
                runner.test_cases = [tc for tc in runner.test_cases if tc.name in quick_tests]
            
            print(f"Running {len(runner.test_cases)} test scenarios...")
            reports = runner.run_all_tests()
            runner.print_summary()
            
            # Exit with error code if any tests failed
            failed_tests = sum(1 for r in reports if r.result.value in ["FAIL", "ERROR"])
            sys.exit(1 if failed_tests > 0 else 0)
        
        if args.scenario:
            from hyperpod_tui.test_scenarios import run_specific_test
            success = run_specific_test(args.scenario, verbose=args.verbose)
            sys.exit(0 if success else 1)
        
        if args.key_seq:
            from hyperpod_tui.test_framework import KeySequenceSimulator, MockStdscr
            from hyperpod_tui.main import HyperPodTUI
            
            print(f"Running TUI with key sequence: {args.key_seq}")
            
            simulator = KeySequenceSimulator(args.key_seq)
            mock_stdscr = MockStdscr(simulator)
            
            tui = HyperPodTUI(mock_stdscr, test_mode=True)
            tui.run()
            
            print("Test completed successfully")
            if args.verbose:
                print("\nScreen output buffer (last 20 lines):")
                for line in mock_stdscr.output_buffer[-20:]:
                    print(f"  {line}")
            return
        
        # If no specific arguments, show help
        parser.print_help()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()