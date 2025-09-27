# HyperPod TUI Automated Testing

This document describes the automated testing system for HyperPod TUI, which allows you to test the application without manual interaction by simulating keyboard inputs.

## Overview

The testing system consists of several components:

1. **Test Framework** (`test_framework.py`) - Core testing infrastructure
2. **Test Scenarios** (`test_scenarios.py`) - Predefined test cases
3. **Test Runner** (`test_tui.py`) - Command-line test execution
4. **Integration** - Built into main application with `--test-key-seq` argument

## Quick Start

### List Available Tests
```bash
python test_tui.py --list
```

### Run All Tests
```bash
python test_tui.py --all
```

### Run Quick Tests Only
```bash
python test_tui.py --all --quick
```

### Run Specific Test
```bash
python test_tui.py --scenario basic_navigation
```

### Run with Custom Key Sequence
```bash
python test_tui.py --key-seq "<DOWN><DOWN><ENTER>q"
```

### Run with Verbose Output
```bash
python test_tui.py --all --verbose
```

## Using the Main Application

You can also run tests directly through the main application:

```bash
# Run with key sequence
python run.py --test-key-seq "<DOWN><ENTER>q"

# Run specific scenario
python run.py --test-scenario basic_navigation

# List available scenarios
python run.py --list-tests

# Run all tests
python run.py --run-all-tests --verbose
```

## Key Sequence Format

The key sequence format supports both regular characters and special keys:

### Regular Characters
```
"hello"     # Types 'hello'
"q"         # Types 'q' (quit)
"123"       # Types '123'
```

### Special Keys
Special keys are enclosed in angle brackets:

```
"<ENTER>"     # Enter key
"<UP>"        # Up arrow
"<DOWN>"      # Down arrow
"<LEFT>"      # Left arrow
"<RIGHT>"     # Right arrow
"<BACKSPACE>" # Backspace
"<DELETE>"    # Delete key
"<HOME>"      # Home key
"<END>"       # End key
"<PAGEUP>"    # Page Up
"<PAGEDOWN>"  # Page Down
"<TAB>"       # Tab key
"<SPACE>"     # Space bar
"<ESC>"       # Escape key
"<F1>"        # Function keys F1-F12
```

### Search Mode Keys
The TUI now supports incremental search mode:

```
"f"           # Enter search mode
"<ESC>"       # Exit search mode (cancel)
"<ENTER>"     # Exit search mode (select)
```

In search mode:
- Type characters to filter results
- Use `<UP>` and `<DOWN>` to navigate filtered results
- `<BACKSPACE>` removes characters from search
- `<ENTER>` selects current item and exits search mode
- `<ESC>` cancels search and exits search mode

### Escape Sequences
```
"\\n"         # Newline
"\\t"         # Tab
"\\r"         # Carriage return
"\\\\"        # Literal backslash
```

### Complex Examples
```bash
# Navigate and use new search mode
python test_tui.py --key-seq "<DOWN><DOWN>f test<ENTER>q"

# Multi-level navigation
python test_tui.py --key-seq "<DOWN><ENTER><DOWN><ENTER><BACKSPACE><BACKSPACE>q"

# Search mode with cancel
python test_tui.py --key-seq "f production<ESC>f dev<ENTER>q"

# Old-style filter clearing (still works)
python test_tui.py --key-seq "f test<DELETE>q"
```

## Predefined Test Scenarios

### Available Scenarios

1. **quick_exit** - Test immediate exit
2. **basic_navigation** - Basic navigation through screens
3. **filter_functionality** - Test filtering features
4. **keyboard_shortcuts** - Test keyboard shortcuts
5. **drill_down_navigation** - Test hierarchical navigation
6. **edge_cases** - Test edge cases and error conditions
7. **stress_test** - Rapid key presses and navigation
8. **comprehensive_workflow** - Complete workflow test

### Scenario Details

#### Basic Navigation
Tests navigation through the TUI hierarchy:
- Navigate up/down in cluster list
- Enter cluster to view instance groups
- Enter instance group to view instances
- Navigate back through screens
- Exit application

#### Filter Functionality
Tests filtering capabilities:
- Apply text filters
- Clear filters with DELETE and 'x' keys
- Type and backspace in filters
- Filter behavior across different screens

#### Keyboard Shortcuts
Tests various keyboard shortcuts:
- HOME/END keys for first/last items
- PAGE UP/DOWN for pagination
- Refresh with 'r' key
- Details pane expansion/shrinking with {/}

## Creating Custom Tests

### Simple Test Case

```python
from hyperpod_tui.test_framework import TestCase, TestStep

my_test = TestCase(
    name="my_custom_test",
    description="My custom test description",
    steps=[
        TestStep("", "Start application"),
        TestStep("<DOWN>", "Navigate down"),
        TestStep("filter", "Apply filter"),
        TestStep("q", "Quit"),
    ]
)
```

### Test Case with Validation

```python
def validate_on_cluster_screen(app, mock_stdscr):
    """Validate we're on the cluster screen."""
    return hasattr(app.current_screen, 'clusters')

my_test = TestCase(
    name="validated_test",
    description="Test with validation",
    steps=[
        TestStep("", "Start", validator=validate_on_cluster_screen),
        TestStep("q", "Quit"),
    ]
)
```

### Running Custom Tests

```python
from hyperpod_tui.test_framework import TUITestRunner
from hyperpod_tui.main import HyperPodTUI

runner = TUITestRunner(HyperPodTUI, verbose=True)
runner.add_test_case(my_test)
reports = runner.run_all_tests()
runner.print_summary()
```

## Test Framework Components

### TestStep
Represents a single test step:
- `keys`: Key sequence to send
- `description`: Human-readable description
- `delay_ms`: Delay after step (default: 100ms)
- `validator`: Optional validation function
- `expected_screen`: Optional expected screen type

### TestCase
Represents a complete test:
- `name`: Unique test name
- `description`: Test description
- `steps`: List of TestStep objects
- `setup`: Optional setup function
- `teardown`: Optional cleanup function

### TestReport
Contains test execution results:
- `test_name`: Name of executed test
- `result`: PASS/FAIL/SKIP/ERROR
- `duration_ms`: Execution time
- `error_message`: Error details if failed
- `steps_executed`: Number of completed steps
- `total_steps`: Total number of steps

### TUITestRunner
Executes tests:
- `add_test_case()`: Add test to runner
- `run_test_case()`: Run single test
- `run_all_tests()`: Run all added tests
- `print_summary()`: Print execution summary

## Best Practices

### Test Design
1. **Keep tests focused** - Each test should verify specific functionality
2. **Use descriptive names** - Test and step names should be clear
3. **Add validation** - Use validators to ensure tests work correctly
4. **Handle timing** - Add appropriate delays for UI updates
5. **Test edge cases** - Include boundary conditions and error scenarios

### Key Sequences
1. **Start simple** - Begin with basic navigation
2. **Add delays** - Allow time for screen updates
3. **Test cleanup** - Always end with quit ('q')
4. **Use special keys** - Leverage HOME, END, PAGE UP/DOWN
5. **Test filters** - Include filter application and clearing

### Debugging
1. **Use verbose mode** - See detailed execution information
2. **Check output buffer** - Review screen output in verbose mode
3. **Add validation** - Verify application state at key points
4. **Test incrementally** - Build complex tests from simple ones
5. **Handle errors gracefully** - Include error recovery in tests

## Integration with CI/CD

### Exit Codes
- `0`: All tests passed
- `1`: One or more tests failed or error occurred

### Example CI Script
```bash
#!/bin/bash
# Run quick tests
python test_tui.py --all --quick
if [ $? -ne 0 ]; then
    echo "Quick tests failed"
    exit 1
fi

# Run full test suite
python test_tui.py --all
if [ $? -ne 0 ]; then
    echo "Full test suite failed"
    exit 1
fi

echo "All tests passed"
```

### GitHub Actions Example
```yaml
name: TUI Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run TUI tests
      run: python test_tui.py --all --verbose
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from project root
   - Check Python path configuration

2. **Test Timeouts**
   - Increase delay_ms in test steps
   - Check for infinite loops in application

3. **Validation Failures**
   - Verify validator functions are correct
   - Check application state expectations

4. **Key Sequence Issues**
   - Verify special key format (`<KEY>`)
   - Check for typos in key names
   - Test sequences manually first

### Debug Mode
Run with verbose output to see detailed execution:
```bash
python test_tui.py --scenario basic_navigation --verbose
```

This will show:
- Each test step execution
- Validation results
- Screen output buffer
- Timing information
- Error details

## Examples

See `examples/test_examples.py` for complete examples of:
- Creating custom test cases
- Using validation functions
- Running tests programmatically
- Handling test results