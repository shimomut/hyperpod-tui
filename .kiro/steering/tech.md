# Technology Stack

## Language & Runtime
- **Python 3.x** - Primary development language
- Cross-platform compatibility (Windows, macOS, Linux)

## Key Technologies
- **Terminal User Interface (TUI)** - Interactive command-line interface
- **AWS SDK/Boto3** - AWS HyperPod API integration
- **AWS HyperPod** - Target service for cluster management

## Development Environment
- Python virtual environments supported (.venv, venv/, env/)
- Multiple package managers supported:
  - pip (requirements.txt)
  - Poetry (poetry.lock)
  - UV (uv.lock)
  - PDM (pdm.lock)
  - Pipenv (Pipfile.lock)

## Common Commands
Since this is an early-stage project, specific build/test commands are not yet established. Standard Python development workflow applies:

```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (when available)
pip install -r requirements.txt
# or
pip install -e .

# Run the application (when implemented)
python -m hyperpod_tui
# or
hyperpod-tui

# Testing (when implemented)
pytest
# or
python -m pytest

# Linting and formatting
ruff check .
ruff format .
```

## Code Quality Tools
- **Ruff** - Fast Python linter and formatter (indicated by .ruff_cache/ in .gitignore)
- **MyPy** - Static type checking (indicated by .mypy_cache/ in .gitignore)
- **Pytest** - Testing framework (indicated by .pytest_cache/ in .gitignore)