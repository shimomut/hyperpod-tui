# Project Structure

## Current Organization
This is an early-stage project with minimal structure established. The current layout follows standard Python project conventions:

```
hyperpod-tui/
├── .git/                   # Git version control
├── .gitignore             # Git ignore patterns (Python-focused)
├── .kiro/                 # Kiro AI assistant configuration
│   └── steering/          # AI guidance documents
├── LICENSE                # MIT License
└── README.md              # Project documentation
```

## Expected Structure (To Be Implemented)
Based on the project goals and Python conventions, the following structure is recommended:

```
hyperpod-tui/
├── src/
│   └── hyperpod_tui/      # Main package directory
│       ├── __init__.py    # Package initialization
│       ├── main.py        # Application entry point
│       ├── cli/           # Command-line interface components
│       ├── tui/           # Terminal UI components
│       ├── aws/           # AWS HyperPod integration
│       └── utils/         # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
├── pyproject.toml         # Project configuration and dependencies
├── requirements.txt       # Alternative dependency specification
└── README.md              # Project documentation
```

## Naming Conventions
- **Package/Module Names**: Use lowercase with underscores (snake_case)
- **Class Names**: Use PascalCase
- **Function/Variable Names**: Use lowercase with underscores (snake_case)
- **Constants**: Use UPPERCASE with underscores
- **File Names**: Use lowercase with underscores, match module names

## Key Directories
- `src/hyperpod_tui/` - Main application code
- `tests/` - Unit and integration tests
- `docs/` - Documentation and guides
- `examples/` - Sample configurations and usage examples

## Configuration Files
- `pyproject.toml` - Modern Python project configuration (preferred)
- `requirements.txt` - Dependency specification (alternative/additional)
- `.gitignore` - Already configured for Python development
- `LICENSE` - MIT License (already present)