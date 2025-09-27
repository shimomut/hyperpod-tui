# Technology Stack

## Language & Runtime
- **Python 3.x** - Primary development language
- Cross-platform compatibility (Windows, macOS, Linux)

## Key Technologies
- **Python curses module** - Terminal User Interface (TUI) implementation
- **boto3** - AWS SDK for Python to access SageMaker HyperPod APIs
- **AWS SageMaker HyperPod** - Target service for cluster management
- Cross-platform TUI support (macOS, Windows, Linux)

## Core Dependencies
- **curses** - Built-in Python module for TUI development
- **boto3** - AWS SDK for Python (SageMaker HyperPod integration)
- **botocore** - Low-level AWS service access (dependency of boto3)

## Development Environment
- Python virtual environments supported (.venv, venv/, env/)
- AWS credentials configuration required (AWS CLI, environment variables, or IAM roles)
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
pip install boto3  # Core AWS SDK dependency
pip install -r requirements.txt
# or
pip install -e .

# Configure AWS credentials (required for boto3)
aws configure
# or set environment variables:
# export AWS_ACCESS_KEY_ID=your_key
# export AWS_SECRET_ACCESS_KEY=your_secret
# export AWS_DEFAULT_REGION=us-east-1

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