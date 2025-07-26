# Contributing to TextualMD

Thank you for your interest in contributing to TextualMD! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

1. Python 3.13 or higher
2. [uv](https://github.com/astral-sh/uv) package manager

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setting Up Your Development Environment

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/phunt/textualMD.git
   cd textualMD
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. Install the package in editable mode for development:
   ```bash
   uv pip install -e .
   ```

   Or install globally in editable mode:
   ```bash
   uv tool install . --force --editable
   ```

### Running the Application

During development, you can run the application in several ways:

```bash
# Using uv run (recommended for testing)
uv run tmd README.md

# If you have the venv activated
python -m textualmd README.md

# If installed globally with --editable
tmd README.md
```

## Making Changes

### Code Structure

- `src/textualmd/` - Main package directory
  - `app.py` - Main application logic
  - `main.py` - Entry point
  - `constants.py` - Application constants
  - `app_types.py` - Type definitions
  - `services/` - Core services (file management, search, etc.)
  - `ui/` - User interface components

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all public functions and classes
- Keep line length under 88 characters (Black's default)

### Testing Your Changes

Before submitting:

1. Ensure the application runs without errors
2. Test all affected features
3. Verify keyboard shortcuts still work
4. Check that file watching, search, and export features function correctly

### Adding Dependencies

To add a new dependency:

```bash
# Add a runtime dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

## Submitting Changes

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with clear, descriptive messages:
   ```bash
   git add .
   git commit -m "Add feature: description of what you added"
   ```

3. Push your branch and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

4. In your pull request description, please include:
   - What changes you made and why
   - How to test your changes
   - Any screenshots if UI changes are involved
   - Reference any related issues

## Reporting Issues

When reporting issues, please include:

- Your operating system and Python version
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Any error messages or stack traces
- Screenshots if applicable

## Feature Requests

Feel free to open an issue to discuss new features. Check the `TODO.md` file for already planned features.

## Questions?

If you have questions about contributing, feel free to open an issue for discussion.

Thank you for contributing to TextualMD! 