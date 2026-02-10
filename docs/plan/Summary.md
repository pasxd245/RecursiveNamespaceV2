# RecursiveNamespaceV2 - Project Summary

## Overview

**RecursiveNamespaceV2** is a Python library that extends Python's built-in `SimpleNamespace` class to provide enhanced functionality for working with nested namespaces and dictionaries. It offers an intuitive, Pythonic way to access and manipulate deeply nested data structures with both dictionary-style and attribute-style access patterns.

### Project Information

- **Package Name**: RecursiveNamespaceV2
- **Repository**: <https://github.com/pasxd245/RecursiveNamespaceV2>
- **Author**: VienPQ (<pasxd245@gmail.com>)
- **License**: MIT License
- **Python Support**: Python 3.8+
- **Dependencies**: None (pure Python)

## Core Features

### 1. Recursive Namespace Conversion

The library automatically converts nested dictionaries into recursive namespaces, allowing seamless traversal of complex data structures.

```python
from recursivenamespace import RNS

data = {
    'name': 'John',
    'address': {
        'city': 'Anytown',
        'street': '123 Main St'
    }
}

rn = RNS(data)
print(rn.address.city)  # Anytown
```

### 2. Dual Access Pattern

Access elements using either dictionary keys or namespace attributes interchangeably:

```python
rn.address.city == rn['address']['city']  # True
rn.address['city'] == rn['address'].city  # True
```

### 3. Chain-Key Access

Advanced key access using dot notation for nested structures:

```python
# Set nested values using chain keys
rn.val_set("address.city", "New City")

# Get nested values using chain keys
city = rn.val_get("address.city")
```

### 4. Array Indexing Support

Special syntax for working with arrays within namespaces:

- `key[].0` - Access element at index 0
- `key[].#` - Access last element or append to array
- `key[].-1` - Access last element
- `key[].#.subkey` - Append new object with subkey to array

```python
rn.val_set("friends[].#", "New Friend")  # Append to array
rn.val_set("items[].0.name", "Item 1")   # Set nested array element
```

### 5. Bidirectional Conversion

Easy conversion between dictionaries and namespaces:

```python
# Dict to RNS
rn = RNS(data)

# RNS back to dict
data = rn.to_dict()

# Flatten nested structures
flat_dict = rn.to_dict(flatten_sep='_')
# {'address_city': 'Anytown', 'address_street': '123 Main St'}
```

### 6. Key Normalization

Automatically handles special characters in keys:

```python
rn['some-key'] = 'value'
print(rn.some_key)  # 'value' - hyphens converted to underscores

# Can disable with use_raw_key=True
rn_raw = RNS(data, use_raw_key=True)
```

### 7. Dynamic Field Addition

Add fields on the fly with automatic nested namespace creation:

```python
rn.new_field = 'value'
rn.nested.new_field = 'also works'  # Creates nested namespace automatically
```

## Architecture

### Project Structure

```text
RecursiveNamespaceV2/
├── src/
│   └── recursivenamespace/
│       ├── __init__.py           # Package exports
│       ├── main.py               # Core recursivenamespace class
│       ├── utils.py              # Utility functions
│       └── _version.py           # Version management
├── tests/
│   ├── test_recursive_namespace.py
│   ├── test_rns_v2.py
│   └── test_utils.py
├── examples/
│   ├── basic_usage.py
│   ├── nested_namespace.py
│   ├── keys_vs_attributes.py
│   └── click_package.py
├── pyproject.toml                # Project configuration
├── setup.py                      # Setup script
└── README.md
```

### Core Components

#### 1. recursivenamespace Class ([src/recursivenamespace/main.py](../src/recursivenamespace/main.py))

The main class that extends `SimpleNamespace` with the following key methods:

- `__init__(data, accepted_iter_types, use_raw_key)` - Initialize with dict or kwargs
- `val_set(key, value)` - Set value using chain-key notation
- `val_get(key)` - Get value using chain-key notation
- `get_or_else(key, or_else)` - Safe get with default value
- `to_dict(flatten_sep)` - Convert to dictionary (optionally flattened)
- `update(data)` - Update namespace with new data
- `as_schema(schema_cls)` - Convert to dataclass schema
- `items()`, `keys()`, `values()` - Dictionary-like iteration
- `copy()`, `deepcopy()` - Copying operations

#### 2. Utility Module ([src/recursivenamespace/utils.py](../src/recursivenamespace/utils.py))

Provides helper functions for key manipulation:

- `escape_key(key)` / `unescape_key(key)` - Handle special characters in keys
- `split_key(key)` / `join_key(parts)` - Parse and construct chain keys
- `flatten_as_dict(data, sep)` - Flatten nested dictionaries
- `flatten_as_list(data, flat_list_type)` - Flatten to key-value pairs
- `KV_Pair` - Named tuple for key-value pairs
- `FlatListType` - Enum for list flattening strategies

#### 3. Protected Keys System

The class maintains internal state with protected keys that cannot be accessed or modified by users:

- `__key_` - Internal key name
- `__use_raw_key_` - Flag for key normalization
- `__supported_types_` - List of supported iterable types
- `__protected_keys_` - Set of protected attribute names

### Advanced Features

#### RNS Decorator

Function decorator for creating RNS objects from function returns or dataclasses:

```python
from recursivenamespace import rns

@rns.rns()
def create_config():
    return {'setting1': 'value1', 'setting2': 'value2'}

config = create_config()  # Returns RNS object
```

With chain-key support:

```python
@rns.rns(use_chain_key=True)
def create_nested():
    return {"x.y.z": [1, 2, 3]}  # Creates nested structure

result = create_nested()
print(result.x.y.z)  # [1, 2, 3]
```

#### Schema Conversion

Convert RNS objects to dataclass schemas:

```python
import dataclasses
from recursivenamespace import RNS

@dataclasses.dataclass
class Config:
    name: str
    value: int

rn = RNS({'name': 'test', 'value': 42})
config = rn.as_schema(Config)  # Returns Config dataclass instance
```

#### Pickle Support

Full serialization support for saving and loading RNS objects:

```python
import pickle

# Save
with open('data.pkl', 'wb') as f:
    pickle.dump(rn, f)

# Load
with open('data.pkl', 'rb') as f:
    rn = pickle.load(f)
```

## Use Cases

### 1. Configuration Management

Manage application configurations with nested settings:

```python
config = RNS({
    'database': {
        'host': 'localhost',
        'port': 5432,
        'credentials': {'user': 'admin', 'password': 'secret'}
    },
    'api': {
        'timeout': 30,
        'retries': 3
    }
})

# Easy access
db_host = config.database.host
timeout = config.api.timeout
```

### 2. YAML/JSON Data Processing

Work with loaded YAML or JSON data structures:

```python
import yaml
from recursivenamespace import RNS

with open('config.yaml') as f:
    data = yaml.safe_load(f)

config = RNS(data)
# Access nested YAML structure easily
print(config.server.host)
```

### 3. ML Experiment Tracking

Track machine learning experiments with nested parameters and metrics:

```python
experiment = RNS(
    params=RNS(
        learning_rate=0.001,
        batch_size=32,
        optimizer='adam'
    ),
    metrics=RNS(
        accuracy=0.95,
        f1_score=0.93
    )
)

# Flatten for logging
flat_results = experiment.to_dict(flatten_sep='_')
# {'params_learning_rate': 0.001, 'metrics_accuracy': 0.95, ...}
```

### 4. API Response Handling

Simplify working with nested API responses:

```python
api_response = RNS({
    'user': {
        'id': 123,
        'profile': {
            'name': 'John',
            'email': 'john@example.com'
        }
    }
})

user_email = api_response.user.profile.email
```

## Technical Details

### Build System

- **Build Backend**: Setuptools (PEP 517 compliant with versioneer support)
- **Package Manager**: uv (fast Rust-based package manager)
- **Version Management**: Versioneer (Git-based versioning)
- **Tag Prefix**: `v` (e.g., v1.0.0)
- **Version Style**: PEP 440 compliant

### Testing

- **Framework**: pytest
- **Coverage**: pytest-cov
- **Test Structure**:
  - Unit tests for core functionality
  - Integration tests for complex scenarios
  - Pickle/serialization tests
  - Decorator and schema conversion tests

Run tests:

```bash
pytest -s
# With coverage
coverage run -m pytest
```

### Code Quality Tools

- **Formatter/Linter**: Ruff (80 character line length)
- **Target Python**: 3.10 for tooling
- **Spell Check**: codespell (ignores "rns")

### Aliases and Imports

The package provides multiple import aliases for convenience:

```python
from recursivenamespace import recursivenamespace  # Full name
from recursivenamespace import RecursiveNamespace  # Pascal case
from recursivenamespace import RNS                 # Short alias
from recursivenamespace import rns                 # Module access
```

## Key Differences from SimpleNamespace

| Feature                 | SimpleNamespace | RecursiveNamespace |
| ----------------------- | --------------- | ------------------ |
| Nested dict conversion  | Manual          | Automatic          |
| Dict-style access       | No              | Yes                |
| Chain-key access        | No              | Yes                |
| Array indexing          | No              | Yes                |
| to_dict() method        | No              | Yes                |
| Flatten support         | No              | Yes                |
| Key normalization       | No              | Yes (optional)     |
| Dynamic nested creation | No              | Yes                |
| Protected keys          | No              | Yes                |
| Schema conversion       | No              | Yes                |

## Error Handling

The library provides custom exceptions for specific error cases:

- `SetChainKeyError` - Raised when attempting to set a chain-key on incompatible types
- `GetChainKeyError` - Raised when attempting to get a chain-key from incompatible types
- `KeyError` - Raised for protected key access or missing keys

## Performance Considerations

- **Lightweight**: No external dependencies
- **Lazy Processing**: Only processes nested structures as needed
- **Memory Efficient**: Uses Python's built-in `SimpleNamespace` as base
- **Copy Operations**: Supports both shallow (`copy()`) and deep (`deepcopy()`) copying

## Version Information

Version is managed through Git tags using Versioneer:

- Development version: Derived from Git commit
- Release version: Set via Git tags (e.g., `v1.0.0`)
- Version file: `_version.py` (auto-generated)

## Installation

**From PyPI:**

```bash
pip install RecursiveNamespaceV2
```

**From Source:**

```bash
git clone https://github.com/pasxd245/RecursiveNamespaceV2.git
cd RecursiveNamespaceV2
pip install -e .
```

## Contributing

The project welcomes contributions with these guidelines:

- All pull requests should include tests
- Follow existing code style (Ruff configured)
- Update documentation for new features
- Ensure all tests pass before submitting

## Future Enhancements

Based on the codebase, potential areas for future development:

- Type hints for better IDE support
- Additional serialization formats (JSON, TOML)
- Performance optimizations for large datasets
- More comprehensive documentation
- Additional utility methods for common operations

## Conclusion

RecursiveNamespaceV2 provides a powerful yet lightweight solution for working with nested data structures in Python. Its automatic recursive conversion, dual access patterns, and advanced features like chain-key access make it ideal for configuration management, data processing, and any scenario involving complex nested dictionaries.

---

**Generated**: 2026-01-31
**Project Version**: Git-managed via Versioneer
