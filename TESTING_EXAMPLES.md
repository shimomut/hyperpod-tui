# HyperPod TUI Testing Examples

This document provides practical examples of using the automated testing system.

## Quick Start Examples

### 1. Simple Key Sequence Tests

Test immediate quit:
```bash
python run.py --test-key-seq 'q'
```

Test navigation and quit:
```bash
python run.py --test-key-seq '<DOWN><DOWN><UP>q'
```

Test filtering:
```bash
python run.py --test-key-seq 'test<DELETE>q'
```

Test complex workflow:
```bash
python run.py --test-key-seq '<DOWN>prod<ENTER><BACKSPACE>q'
```

### 2. Predefined Test Scenarios

List all available tests:
```bash
python run.py --list-tests
```

Run a specific test:
```bash
python run.py --test-scenario quick_exit
```

Run all tests:
```bash
python run.py --run-all-tests
```

### 3. Using the Test Runner

The dedicated test runner provides more options:

```bash
# List tests
python test_tui.py --list

# Run all tests
python test_tui.py --all

# Run quick tests only
python test_tui.py --all --quick

# Run with verbose output
python test_tui.py --all --verbose

# Run specific test
python test_tui.py --scenario basic_navigation

# Custom key sequence
python test_tui.py --key-seq '<DOWN><DOWN>hello<DELETE>q'
```

## Key Sequence Reference

### Regular Keys
- `q` - Quit application
- `r` - Refresh data
- `x` - Clear filter
- `hello` - Type text "hello"

### Special Keys (in angle brackets)
- `<ENTER>` - Enter key
- `<UP>`, `<DOWN>` - Arrow keys
- `<LEFT>`, `<RIGHT>` - Arrow keys
- `<BACKSPACE>` - Backspace key
- `<DELETE>` - Delete key
- `<HOME>`, `<END>` - Home/End keys
- `<PAGEUP>`, `<PAGEDOWN>` - Page navigation
- `<TAB>` - Tab key
- `<SPACE>` - Space bar
- `<ESC>` - Escape key
- `<F1>` through `<F12>` - Function keys

### Complex Examples

Navigate and filter:
```bash
python run.py --test-key-seq '<DOWN><DOWN>production<DELETE><UP>q'
```

Multi-level navigation:
```bash
python run.py --test-key-seq '<DOWN><ENTER><DOWN><ENTER><BACKSPACE><BACKSPACE>q'
```

Stress test navigation:
```bash
python run.py --test-key-seq '<DOWN><UP><DOWN><UP><DOWN><UP>q'
```

Filter operations:
```bash
python run.py --test-key-seq 'test<BACKSPACE><BACKSPACE><BACKSPACE><BACKSPACE>prod<DELETE>q'
```

## Available Test Scenarios

1. **quick_exit** - Test immediate application exit
2. **basic_navigation** - Navigate through TUI screens
3. **filter_functionality** - Test filtering and search features
4. **keyboard_shortcuts** - Test all keyboard shortcuts
5. **drill_down_navigation** - Test hierarchical navigation
6. **edge_cases** - Test boundary conditions
7. **stress_test** - Rapid input testing
8. **comprehensive_workflow** - Complete end-to-end test

## Verbose Output

Add `--verbose` to see detailed execution information:

```bash
python run.py --test-scenario basic_navigation --verbose
```

This shows:
- Each test step execution
- Timing information
- Screen output buffer
- Error details if any

## Integration with CI/CD

The testing system returns appropriate exit codes:
- `0` - All tests passed
- `1` - One or more tests failed

Example CI script:
```bash
#!/bin/bash
# Run quick tests first
python test_tui.py --all --quick
if [ $? -ne 0 ]; then
    echo "Quick tests failed"
    exit 1
fi

# Run full test suite
python test_tui.py --all
exit $?
```

## Creating Custom Tests

You can create custom key sequences for specific testing needs:

```bash
# Test specific workflow
python run.py --test-key-seq '<DOWN><DOWN>cluster-name<ENTER><DOWN>instance-group<ENTER><UP><BACKSPACE><BACKSPACE>q'

# Test error conditions
python run.py --test-key-seq '<UP><UP><UP><DOWN><DOWN><DOWN>q'

# Test rapid input
python run.py --test-key-seq 'abcdefg<BACKSPACE><BACKSPACE><BACKSPACE>xyz<DELETE>q'
```

## Demo Script

Run the demo to see all available options:

```bash
python demo_test.py
```

Run a sample test:
```bash
python demo_test.py --run-sample
```

This automated testing system allows you to:
- Test the TUI without manual interaction
- Verify functionality across different scenarios
- Integrate testing into CI/CD pipelines
- Debug issues with verbose output
- Create custom test workflows