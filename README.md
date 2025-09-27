# HyperPod TUI

A Terminal User Interface (TUI) application for browsing and manipulating AWS SageMaker HyperPod clusters.

## Features

- **Interactive cluster browsing**: Navigate through clusters, instance groups, and instances
- **Hierarchical navigation**: Drill down with Enter, go back with Backspace
- **Dynamic filtering**: Filter resources using Python fnmatch patterns
- **Configurable interface**: Customizable key bindings and UI settings
- **Resizable panes**: Adjust the details pane height with `{` and `}` keys
- **Cross-platform**: Works on macOS, Linux, and Windows

## Installation

### Prerequisites

- Python 3.8 or higher
- AWS credentials configured (via AWS CLI, environment variables, or IAM roles)

### Install from source

```bash
# Clone the repository
git clone https://github.com/your-org/hyperpod-tui.git
cd hyperpod-tui

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Windows users

On Windows, you'll need the `windows-curses` package:

```bash
pip install windows-curses
```

## AWS Setup

### Configure AWS Credentials

The application connects to real AWS SageMaker HyperPod clusters. You need to configure your AWS credentials using one of these methods:

#### Option 1: AWS CLI (Recommended)
```bash
aws configure
```

#### Option 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### Option 3: IAM Roles (for EC2 instances)
If running on an EC2 instance, attach an IAM role with the required permissions.

### Test Your Connection

Before using the TUI, test your AWS connection:

```bash
python test_aws_integration.py
```

## Usage

### Basic Usage

```bash
# Run the application
hyperpod-tui

# Or run directly with Python
python -m hyperpod_tui.main
```

### Navigation

- **Enter**: Drill down into selected resource (Clusters → Instance Groups → Instances)
- **Backspace**: Go back to parent level
- **↑/↓ or k/j**: Navigate up/down in the list
- **Page Up/Down**: Navigate by page
- **Home/End**: Go to first/last item
- **q**: Quit the application
- **r**: Refresh data from AWS

### Interface Controls

- **Filter box**: Type to filter resources using fnmatch patterns (e.g., `*prod*`, `test-*`)
- **{ key**: Shrink details pane
- **} key**: Expand details pane
- **Del/x**: Clear current filter

### Screen Layout

```
┌─ Header ─────────────────────────────────────────────────────┐
├─ Filter: [type here to filter]                               │
├─ Resource List ──────────────────────────────────────────────┤
│ ● cluster-1                    InService                     │
│ ○ cluster-2                    Creating                      │
│ ● cluster-3                    InService                     │
├─ Resource Details ───────────────────────────────────────────┤
│   Name: cluster-1                                            │
│   Status: InService                                          │
│   Created: 2024-01-15 10:30:00                              │
│   Instance Groups: 2 groups                                 │
├─ Footer ─────────────────────────────────────────────────────┤
│ q:Quit  Enter:Select  Backspace:Back  {:Shrink  }:Expand    │
│ ↑↓:Navigate  PgUp/PgDn:Page  Home/End:First/Last  x:Clear   │
└──────────────────────────────────────────────────────────────┘
```

## Configuration

The application creates a configuration file at `~/.hyperpod-tui/config.json` on first run.

### Key Bindings

All key bindings are configurable in the config file:

```json
{
  "key_bindings": {
    "quit": ["q", "Q"],
    "enter": ["\n", "\r"],
    "back": ["\b", "KEY_BACKSPACE"],
    "expand_details": ["}"],
    "shrink_details": ["{"],
    "up": ["KEY_UP", "k"],
    "down": ["KEY_DOWN", "j"],
    "refresh": ["r", "R", "KEY_F5"]
  }
}
```

### UI Settings

```json
{
  "ui": {
    "default_details_height": 0.3,
    "min_details_height": 3,
    "max_details_height": 0.8,
    "filter_prompt": "Filter: "
  }
}
```

### AWS Settings

```json
{
  "aws": {
    "region": "us-east-1",
    "profile": null
  }
}
```

## Automated Testing

HyperPod TUI includes a comprehensive automated testing system that simulates keyboard inputs to test the application without manual interaction.

### Quick Testing

```bash
# List available test scenarios
python run.py --list-tests

# Run all tests
python run.py --run-all-tests

# Run a specific test scenario
python run.py --test-scenario basic_navigation

# Test with custom key sequence
python run.py --test-key-seq "<DOWN><DOWN><ENTER>q"
```

### Using the Test Runner

```bash
# Dedicated test runner with more options
python test_tui.py --list                    # List all tests
python test_tui.py --all                     # Run all tests
python test_tui.py --all --quick             # Run quick tests only
python test_tui.py --scenario basic_navigation  # Run specific test
python test_tui.py --key-seq "<DOWN>q"       # Custom key sequence
python test_tui.py --all --verbose           # Verbose output
```

### Key Sequence Format

The testing system supports both regular characters and special keys:

```bash
# Regular characters
"hello"           # Types 'hello'
"q"              # Quit command

# Special keys (in angle brackets)
"<ENTER>"        # Enter key
"<UP><DOWN>"     # Arrow keys
"<BACKSPACE>"    # Backspace
"<DELETE>"       # Delete key
"<HOME><END>"    # Home/End keys
"<PAGEUP>"       # Page navigation

# Complex example
"<DOWN><DOWN>test<DELETE><ENTER>q"  # Navigate, filter, clear, enter, quit
```

### Available Test Scenarios

- **quick_exit**: Test immediate application exit
- **basic_navigation**: Navigate through TUI screens
- **filter_functionality**: Test filtering and search features
- **keyboard_shortcuts**: Test all keyboard shortcuts
- **drill_down_navigation**: Test hierarchical navigation
- **edge_cases**: Test boundary conditions and error handling
- **stress_test**: Rapid input and navigation testing
- **comprehensive_workflow**: Complete end-to-end workflow

### Creating Custom Tests

```python
from hyperpod_tui.test_framework import TestCase, TestStep

my_test = TestCase(
    name="my_test",
    description="Custom test description",
    steps=[
        TestStep("", "Start application"),
        TestStep("<DOWN>", "Navigate down"),
        TestStep("filter", "Apply filter"),
        TestStep("q", "Quit"),
    ]
)
```

See `docs/TESTING.md` for comprehensive testing documentation.

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run automated tests
python test_tui.py --all

# Run linting
ruff check .

# Run type checking
mypy src/
```

### Project Structure

```
src/hyperpod_tui/
├── __init__.py          # Package initialization
├── main.py              # Application entry point
├── config.py            # Configuration management
├── models.py            # Data models
├── aws_client.py        # AWS SageMaker HyperPod client
└── tui.py              # Terminal UI implementation
```

## AWS Permissions

The application requires the following AWS permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:ListClusters",
        "sagemaker:DescribeCluster",
        "sagemaker:ListClusterNodes"
      ],
      "Resource": "*"
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Curses not available on Windows**: Install `windows-curses` package
2. **AWS credentials not found**: Configure AWS CLI or set environment variables
3. **Terminal too small**: Ensure terminal is at least 80x24 characters

### Debug Mode

Set the `HYPERPOD_TUI_DEBUG` environment variable to enable debug logging:

```bash
export HYPERPOD_TUI_DEBUG=1
hyperpod-tui
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Testing AWS Integration

Before running the TUI, you can test your AWS connection:

```bash
# Test AWS integration
python test_aws_integration.py
```

This will verify:
- AWS credentials are properly configured
- You have the necessary permissions
- The application can connect to SageMaker HyperPod
- Any existing clusters in your region

## Roadmap

- [x] Real AWS SageMaker HyperPod API integration
- [ ] Job management interface
- [ ] Log viewing capabilities
- [ ] Cluster creation/deletion
- [ ] Configuration templates
- [ ] Export functionality
- [ ] Plugin system