# Contributing to RecursiveNamespaceV2

Thank you for your interest in contributing to RecursiveNamespaceV2! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- uv (fast Python package manager)

### Setting Up Your Development Environment

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/RecursiveNamespaceV2.git
   cd RecursiveNamespaceV2
   ```

2. **Install uv** (if not already installed)

   ```bash
   # Via install script (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Or via pip
   pip install uv
   ```

3. **Create a virtual environment and install dependencies**

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[test]"
   uv pip install -r requirements.txt
   ```

4. **Install pre-commit hooks**

   ```bash
   uv pip install pre-commit
   pre-commit install
   ```

   This will automatically run code quality checks before each commit.

### Common uv Commands

| Task | Command |
|------|---------|
| Create virtual environment | `uv venv` |
| Install dependencies | `uv pip install -r requirements.txt` |
| Install package editable | `uv pip install -e .` |
| Add dependency | `uv add <package>` |
| Remove dependency | `uv remove <package>` |
| Run tests | `uv run pytest` |
| Build package | `uv build` |

## Development Workflow

### Running Tests

Run the full test suite:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest --cov=src/recursivenamespace --cov-report=term --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
start htmlcov/index.html  # On Windows
```

### Code Quality Checks

The project uses several tools to maintain code quality:

**Linting with Ruff:**

```bash
ruff check src/ tests/
```

**Formatting with Ruff:**

```bash
ruff format src/ tests/
```

**Type checking with mypy:**

```bash
mypy src/recursivenamespace --config-file=pyproject.toml
```

**Spell checking:**

```bash
codespell src/ tests/ README.md
```

**Run all pre-commit hooks manually:**

```bash
pre-commit run --all-files
```

## Code Style Guidelines

### Python Style

- Follow PEP 8 style guide
- Line length: 80 characters (enforced by Ruff)
- Use type hints for all public APIs
- Write docstrings for public functions and classes

### Type Hints

All public APIs must have complete type hints:

```python
from __future__ import annotations
from typing import Any, Optional

def my_function(arg1: str, arg2: Optional[int] = None) -> dict[str, Any]:
    """Function docstring."""
    ...
```

### Testing

- Write tests for all new features
- Maintain test coverage ≥85%
- Use pytest for testing
- Follow existing test patterns

## Submitting Changes

### Before Submitting

1. **Ensure all tests pass**

   ```bash
   pytest -v
   ```

2. **Ensure code quality checks pass**

   ```bash
   ruff check src/ tests/
   ruff format --check src/ tests/
   mypy src/recursivenamespace
   ```

3. **Update documentation** if needed
   - Update README.md for user-facing changes
   - Add docstrings for new functions/classes
   - Update API documentation if applicable

4. **Add tests** for new features or bug fixes

### Commit Messages

Write clear, descriptive commit messages:

```
Add JSON serialization support

- Implement to_json() and from_json() methods
- Add tests for JSON serialization
- Update documentation with examples

Co-Authored-By: Your Name <your.email@example.com>
```

Format:

- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description (wrap at 72 chars)
- Reference issues if applicable: "Fixes #123"

### Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** with clear, atomic commits

3. **Push to your fork**

   ```bash
   git push origin feature/my-new-feature
   ```

4. **Open a Pull Request**
   - Provide a clear description of changes
   - Reference related issues
   - Ensure CI checks pass

5. **Address review feedback**
   - Make requested changes
   - Push updates to your branch
   - Re-request review when ready

## Pull Request Guidelines

### PR Title

Use conventional commit format:

- `feat: Add new feature`
- `fix: Fix bug description`
- `docs: Update documentation`
- `test: Add tests for X`
- `refactor: Refactor code`
- `chore: Update dependencies`

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Test coverage remains ≥85%

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
- [ ] Type hints added for new code
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Python version
- RecursiveNamespaceV2 version
- Operating system
- Minimal code to reproduce the issue
- Expected vs actual behavior
- Full error traceback

### Feature Requests

For feature requests, please describe:

- Use case and motivation
- Proposed API or behavior
- Examples of how it would be used
- Alternatives you've considered

## Code Review Process

- Maintainers will review PRs within 72 hours
- Address feedback promptly
- Be open to suggestions and discussion
- At least one approval required before merging

## Release Process

Releases follow semantic versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

To release a new version:

1. Ensure `main` branch is green (all CI checks pass)
2. Create a git tag: `git tag -a v1.2.3 -m "v1.2.3"`
3. Push the tag: `git push --tags`
4. CI automatically builds, publishes to PyPI, and creates a GitHub Release

## Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Email**: <pasxd245@gmail.com> for private inquiries

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and beginners
- Focus on constructive feedback
- Assume good faith
- Prioritize community well-being

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Other unprofessional conduct

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:

- GitHub contributors page
- Release notes for significant contributions
- Special thanks in project documentation

---

**Thank you for contributing to RecursiveNamespaceV2!** 🎉
