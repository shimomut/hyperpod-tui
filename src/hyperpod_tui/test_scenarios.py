"""Predefined test scenarios for HyperPod TUI."""

from .test_framework import TestCase, TestStep, TUITestRunner
from .main import HyperPodTUI


def validate_cluster_screen(app, mock_stdscr):
    """Validate that we're on the cluster list screen."""
    return hasattr(app.current_screen, 'clusters')


def validate_instance_group_screen(app, mock_stdscr):
    """Validate that we're on the instance group screen."""
    return hasattr(app.current_screen, 'instance_groups')


def validate_instance_screen(app, mock_stdscr):
    """Validate that we're on the instance screen."""
    return hasattr(app.current_screen, 'instances')


def validate_filter_applied(app, mock_stdscr):
    """Validate that a filter has been applied."""
    return len(app.current_screen.filter_text) > 0


def validate_filter_cleared(app, mock_stdscr):
    """Validate that the filter has been cleared."""
    return len(app.current_screen.filter_text) == 0


# Test Scenarios
BASIC_NAVIGATION_TEST = TestCase(
    name="basic_navigation",
    description="Test basic navigation through the TUI screens",
    steps=[
        TestStep("", "Start on cluster list screen", validator=validate_cluster_screen),
        TestStep("<DOWN><DOWN><UP>", "Navigate up and down in cluster list", delay_ms=200),
        TestStep("<ENTER>", "Enter selected cluster", validator=validate_instance_group_screen),
        TestStep("<DOWN><ENTER>", "Navigate to instance group and enter", validator=validate_instance_screen),
        TestStep("<BACKSPACE>", "Go back to instance groups", validator=validate_instance_group_screen),
        TestStep("<BACKSPACE>", "Go back to clusters", validator=validate_cluster_screen),
        TestStep("q", "Quit application", delay_ms=100),
    ]
)

FILTER_TEST = TestCase(
    name="filter_functionality",
    description="Test filtering functionality across screens",
    steps=[
        TestStep("", "Start on cluster list screen", validator=validate_cluster_screen),
        TestStep("test", "Apply filter 'test'", validator=validate_filter_applied),
        TestStep("<DELETE>", "Clear filter with DELETE key", validator=validate_filter_cleared),
        TestStep("prod", "Apply filter 'prod'", validator=validate_filter_applied),
        TestStep("x", "Clear filter with 'x' key", validator=validate_filter_cleared),
        TestStep("dev<BACKSPACE><BACKSPACE><BACKSPACE>", "Type and backspace filter", validator=validate_filter_cleared),
        TestStep("q", "Quit application", delay_ms=100),
    ]
)

KEYBOARD_SHORTCUTS_TEST = TestCase(
    name="keyboard_shortcuts",
    description="Test various keyboard shortcuts and special keys",
    steps=[
        TestStep("", "Start on cluster list screen", validator=validate_cluster_screen),
        TestStep("<HOME>", "Go to first item with HOME key", delay_ms=100),
        TestStep("<END>", "Go to last item with END key", delay_ms=100),
        TestStep("<PAGEUP>", "Page up", delay_ms=100),
        TestStep("<PAGEDOWN>", "Page down", delay_ms=100),
        TestStep("r", "Refresh data", delay_ms=200),
        TestStep("}", "Expand details pane", delay_ms=100),
        TestStep("{", "Shrink details pane", delay_ms=100),
        TestStep("q", "Quit application", delay_ms=100),
    ]
)

DRILL_DOWN_TEST = TestCase(
    name="drill_down_navigation",
    description="Test drilling down through all levels of the hierarchy",
    steps=[
        TestStep("", "Start on cluster list screen", validator=validate_cluster_screen),
        TestStep("<DOWN>", "Select a cluster", delay_ms=100),
        TestStep("<ENTER>", "Enter cluster to view instance groups", validator=validate_instance_group_screen),
        TestStep("<DOWN>", "Select an instance group", delay_ms=100),
        TestStep("<ENTER>", "Enter instance group to view instances", validator=validate_instance_screen),
        TestStep("<UP><DOWN>", "Navigate instances", delay_ms=200),
        TestStep("<BACKSPACE><BACKSPACE>", "Navigate back to clusters", validator=validate_cluster_screen),
        TestStep("q", "Quit application", delay_ms=100),
    ]
)

STRESS_TEST = TestCase(
    name="stress_test",
    description="Stress test with rapid key presses and navigation",
    steps=[
        TestStep("", "Start on cluster list screen", validator=validate_cluster_screen),
        TestStep("<DOWN><DOWN><DOWN><UP><UP><DOWN>", "Rapid navigation", delay_ms=50),
        TestStep("filter<BACKSPACE><BACKSPACE><BACKSPACE><BACKSPACE><BACKSPACE><BACKSPACE>", "Rapid typing and backspace", delay_ms=50),
        TestStep("test<DELETE>", "Type and clear", delay_ms=50),
        TestStep("<ENTER><BACKSPACE>", "Enter and back rapidly", delay_ms=50),
        TestStep("r", "Refresh", delay_ms=100),
        TestStep("q", "Quit application", delay_ms=100),
    ]
)

EDGE_CASES_TEST = TestCase(
    name="edge_cases",
    description="Test edge cases and error conditions",
    steps=[
        TestStep("", "Start on cluster list screen", validator=validate_cluster_screen),
        TestStep("<UP><UP><UP>", "Try to go above first item", delay_ms=100),
        TestStep("<DOWN><DOWN><DOWN><DOWN><DOWN>", "Try to go below last item", delay_ms=100),
        TestStep("<BACKSPACE>", "Try to go back from root screen", delay_ms=100),
        TestStep("invalid_filter_chars!@#$%", "Type special characters in filter", delay_ms=200),
        TestStep("<DELETE>", "Clear filter", delay_ms=100),
        TestStep("q", "Quit application", delay_ms=100),
    ]
)

QUICK_EXIT_TEST = TestCase(
    name="quick_exit",
    description="Test immediate exit without navigation",
    steps=[
        TestStep("q", "Quit immediately", delay_ms=100),
    ]
)

COMPREHENSIVE_TEST = TestCase(
    name="comprehensive_workflow",
    description="Comprehensive test covering all major functionality",
    steps=[
        TestStep("", "Start application", validator=validate_cluster_screen),
        TestStep("<DOWN><DOWN>", "Navigate to second cluster", delay_ms=150),
        TestStep("prod", "Filter for production clusters", validator=validate_filter_applied),
        TestStep("<ENTER>", "Enter filtered cluster", validator=validate_instance_group_screen),
        TestStep("x", "Clear filter in instance groups", validator=validate_filter_cleared),
        TestStep("<DOWN>", "Select instance group", delay_ms=100),
        TestStep("}", "Expand details pane", delay_ms=100),
        TestStep("<ENTER>", "Enter instance group", validator=validate_instance_screen),
        TestStep("{", "Shrink details pane", delay_ms=100),
        TestStep("<PAGEDOWN>", "Page down in instances", delay_ms=100),
        TestStep("web", "Filter instances", validator=validate_filter_applied),
        TestStep("<HOME>", "Go to first filtered instance", delay_ms=100),
        TestStep("r", "Refresh instance data", delay_ms=200),
        TestStep("<DELETE>", "Clear instance filter", validator=validate_filter_cleared),
        TestStep("<BACKSPACE>", "Back to instance groups", validator=validate_instance_group_screen),
        TestStep("<BACKSPACE>", "Back to clusters", validator=validate_cluster_screen),
        TestStep("q", "Quit application", delay_ms=100),
    ]
)


def get_all_test_scenarios():
    """Get all predefined test scenarios."""
    return [
        QUICK_EXIT_TEST,
        BASIC_NAVIGATION_TEST,
        FILTER_TEST,
        KEYBOARD_SHORTCUTS_TEST,
        DRILL_DOWN_TEST,
        EDGE_CASES_TEST,
        STRESS_TEST,
        COMPREHENSIVE_TEST,
    ]


def create_test_runner(verbose: bool = False) -> TUITestRunner:
    """Create a test runner with all predefined scenarios."""
    runner = TUITestRunner(HyperPodTUI, verbose=verbose)
    
    for test_case in get_all_test_scenarios():
        runner.add_test_case(test_case)
    
    return runner


def run_specific_test(test_name: str, verbose: bool = False) -> bool:
    """Run a specific test by name."""
    test_scenarios = {tc.name: tc for tc in get_all_test_scenarios()}
    
    if test_name not in test_scenarios:
        print(f"Test '{test_name}' not found. Available tests:")
        for name in test_scenarios.keys():
            print(f"  - {name}")
        return False
    
    runner = TUITestRunner(HyperPodTUI, verbose=verbose)
    runner.add_test_case(test_scenarios[test_name])
    
    reports = runner.run_all_tests()
    runner.print_summary()
    
    return all(r.result.value == "PASS" for r in reports)


def list_available_tests():
    """List all available test scenarios."""
    print("Available test scenarios:")
    for test_case in get_all_test_scenarios():
        print(f"  {test_case.name}: {test_case.description}")