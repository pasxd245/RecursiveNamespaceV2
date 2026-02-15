# RecursiveNamespaceV2 - Project Promotion

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

---

**Last Updated**: 2026-02-14
**Project Version**: Git-managed via Versioneer
