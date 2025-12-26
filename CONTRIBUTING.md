# Contributing to Klipper Console

Thank you for your interest in contributing to Klipper Console! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and considerate in all interactions. We're all here to make 3D printing better.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

When filing a bug report, include:
- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details**:
  - Python version
  - Operating system
  - Klipper version
  - Moonraker version
- **Error messages** and logs (if applicable)
- **Screenshots** (if relevant)

### Suggesting Features

Feature requests are welcome! Please:
- Check existing issues and PRD.md to see if it's already planned
- Provide a clear use case
- Explain how it aligns with the project goals
- Consider implementation complexity

### Pull Requests

1. **Fork the repository** and create a feature branch
2. **Follow the coding style** (see below)
3. **Write tests** for new functionality
4. **Update documentation** (README.md, docstrings, etc.)
5. **Test your changes** thoroughly
6. **Submit a pull request** with a clear description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Klipper-Console.git
cd Klipper-Console

# Add upstream remote
git remote add upstream https://github.com/darkoperator/Klipper-Console.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

## Coding Standards

### Python Style

- Follow **PEP 8** style guidelines
- Use **type hints** for function signatures
- Maximum line length: **100 characters**
- Use **descriptive variable names**
- Format code with **black**:
  ```bash
  black klipper_console/
  ```

### Documentation

- Write **docstrings** for all public functions and classes
- Use **Google-style** docstrings
- Keep **README.md** and **PRD.md** up to date
- Add **comments** for complex logic

### Example Docstring

```python
def get_sensor(self, name: str) -> TemperatureSensor:
    """
    Get temperature sensor state.

    Args:
        name: Sensor name (with or without prefix)

    Returns:
        TemperatureSensor object with current readings

    Raises:
        ValueError: If sensor not found
    """
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=klipper_console

# Run specific test file
pytest tests/test_handlers.py
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_get_sensor_returns_all_when_no_args()`
- Mock external dependencies (Moonraker API calls)

## Commit Messages

Follow conventional commits format:

```
type(scope): brief description

Detailed explanation (optional)

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring
- `test`: Test additions or fixes
- `chore`: Build process, dependencies

**Examples:**
```
feat(console): add real-time WebSocket streaming

Implemented WebSocket client for live console output.
Includes historical message loading and tab completion.

Fixes #42
```

```
fix(client): increase default timeout to 120s

Long-running operations like homing were timing out.
Increased default from 10s to 120s.

Fixes #56
```

## Project Structure

```
klipper-console/
├── klipper_console/           # Main package
│   ├── cli.py                # Entry point
│   ├── shell.py              # Interactive REPL
│   ├── parser.py             # Command parsing
│   ├── registry.py           # Command registration
│   ├── handlers/             # Command handlers
│   ├── moonraker/            # Moonraker client
│   │   ├── client.py         # HTTP client
│   │   └── websocket_client.py  # WebSocket client
│   ├── models/               # Data models
│   ├── render/               # Output formatting
│   ├── completion/           # Tab completion
│   └── console_viewer.py     # Console viewer
├── tests/                    # Test suite
├── docs/                     # Documentation
├── README.md                 # User documentation
├── PRD.md                    # Product requirements
├── CONTRIBUTING.md           # This file
└── pyproject.toml           # Package configuration
```

## Architecture Guidelines

### Design Principles

1. **Moonraker is the sole integration layer** - No direct Klipper communication
2. **Explicit is better than implicit** - Write operations require clear intent
3. **Safe by default** - Read operations are safe, writes show warnings
4. **Discoverable** - Tab completion and help for everything
5. **Modular** - Separation of concerns between shell, parsing, handlers, rendering

### Adding New Commands

1. **Define the handler** in `handlers/__init__.py`:
   ```python
   def get_widget(self, name: str) -> Widget:
       """Get widget state."""
       # Implementation
   ```

2. **Register in registry** (`registry.py`):
   ```python
   self.register("get_widget", self._get_widget, "Get widget state")
   ```

3. **Add completion support** (`completion/__init__.py`):
   ```python
   elif command == "get_widget":
       candidates = self._cache.get('widgets', [])
   ```

4. **Add rendering** (`render/__init__.py`):
   ```python
   def _render_widget(widget: Widget) -> None:
       # Format and display
   ```

5. **Update documentation** (README.md, docstrings)

6. **Write tests** (`tests/test_handlers.py`)

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Update README.md if needed
4. Create release tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
5. Push tag: `git push origin v0.2.0`

## Questions?

- Open an issue for discussion
- Check PRD.md for project vision and roadmap
- Review existing code for patterns and examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
