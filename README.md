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

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

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

## Roadmap

- [ ] Real AWS SageMaker HyperPod API integration
- [ ] Job management interface
- [ ] Log viewing capabilities
- [ ] Cluster creation/deletion
- [ ] Configuration templates
- [ ] Export functionality
- [ ] Plugin system