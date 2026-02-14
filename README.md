# RecursiveNamespaceV2

[![CI](https://github.com/pasxd245/RecursiveNamespaceV2/workflows/CI/badge.svg)](https://github.com/pasxd245/RecursiveNamespaceV2/actions/workflows/ci.yml)
[![Type Check](https://github.com/pasxd245/RecursiveNamespaceV2/workflows/Type%20Check/badge.svg)](https://github.com/pasxd245/RecursiveNamespaceV2/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/pasxd245/RecursiveNamespaceV2/branch/main/graph/badge.svg)](https://codecov.io/gh/pasxd245/RecursiveNamespaceV2)
[![Python Version](https://img.shields.io/pypi/pyversions/RecursiveNamespaceV2)](https://pypi.org/project/RecursiveNamespaceV2/)
[![PyPI version](https://badge.fury.io/py/RecursiveNamespaceV2.svg)](https://badge.fury.io/py/RecursiveNamespaceV2)
[![License](https://img.shields.io/github/license/pasxd245/RecursiveNamespaceV2)](https://github.com/pasxd245/RecursiveNamespaceV2/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Description

**RecursiveNamespaceV2** extends Python's **SimpleNamespace** to make nested dicts easy to work with using attribute access, dict access, and chain-keys.

Full documentation: [https://recursivenamespacev2.readthedocs.io/](https://recursivenamespacev2.readthedocs.io/)

Key features:

- Recursive conversion of nested dicts/lists
- Attribute and dict access (`rn.a` and `rn["a"]`)
- Chain-key access (`rn.val_get("a.b.c")`)
- Array indexing and append syntax (`items[].0`, `items[].#`)
- Typed, zero-dependency, pure Python

## Installation

To install **RecursiveNamespaceV2** from PyPI:

```bash
pip install RecursiveNamespaceV2
# or with uv
uv pip install RecursiveNamespaceV2
```

For development from source:

```bash
git clone https://github.com/pasxd245/RecursiveNamespaceV2.git
cd RecursiveNamespaceV2
uv venv            # create a virtual environment
uv pip install -e ".[test]"  # install in editable mode with test dependencies
```

## Quick Start

```python
from recursivenamespace import RNS  # or RecursiveNamespace

data = {
    'name': 'John',
    'age': 30,
    'address': {
        'street': '123 Main St',
        'city': 'Anytown'
    },
    'friends': ['Jane', 'Tom']
}

rn = RNS(data)
print(rn.address.city)  # Anytown
print(rn["friends"][1])  # Tom

# Chain-key access
rn.val_set("address.zip", "12345")
print(rn.val_get("address.zip"))  # 12345

# Convert back to dict
data2 = rn.to_dict()
print(data2["address"]["city"])  # Anytown
```

## Examples

See the `examples/` directory for 15 runnable examples organized by difficulty (basic, intermediate, advanced, real-world).

## Testing

To run tests, navigate to the project's root directory and execute:

```bash
uv run pytest -s
# or with coverage:
uv run coverage run -m pytest
# to generate html report:
uv run coverage html
```

## Contributing

Contributions to the **RecursiveNamespace** project are welcome! Please ensure that any pull requests include tests covering new features or fixes. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

## Transparency

AI-assisted development (e.g., Claude Code, Copilot) was used for scaffolding and iteration.
