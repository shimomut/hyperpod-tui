#!/usr/bin/env python3
"""Example test scripts for HyperPod TUI."""

import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from hyperpod_tui.test_framework import TestCase, TestStep, TUITestRunner
from hyperpod_tui.main import HyperPodTUI


def create_custom_test():
    """Create a custom test case example."""
    return TestCase(
        name="custom_example",
        description="Custom test example showing how to create your own tests",
        steps=[
            TestStep("", "Start application", delay_ms=100),
            TestStep("<DOWN><DOWN>", "Navigate down twice", delay_ms=200),
            TestStep("test", "Apply filter 'test'", delay_ms=100),
            TestStep("<DELETE>", "Clear filter", delay_ms=100),
            TestStep("<ENTER>", "Enter selected item", delay_ms=200),
            TestStep("<BACKSPACE>", "Go back", delay_ms=100),
            TestStep("q", "Quit application", delay_ms=100),
        ]
    )


def run_custom_test():
    """Run the custom test."""
    runner = TUITestRunner(HyperPodTUI, verbose=True)
    runner.add_test_case(create_custom_test())
    
    reports = runner.run_all_tests()
    runner.print_summary()
    
    return all(r.result.value == "PASS" for r in reports)


if __name__ == "__main__":
    print("Running custom test example...")
    success = run_custom_test()
    sys.exit(0 if success else 1)