# RecursiveNamespace

[![CI](https://github.com/pasxd245/RecursiveNamespaceV2/workflows/CI/badge.svg)](https://github.com/pasxd245/RecursiveNamespaceV2/actions/workflows/ci.yml)
[![Type Check](https://github.com/pasxd245/RecursiveNamespaceV2/workflows/Type%20Check/badge.svg)](https://github.com/pasxd245/RecursiveNamespaceV2/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/pasxd245/RecursiveNamespaceV2/branch/main/graph/badge.svg)](https://codecov.io/gh/pasxd245/RecursiveNamespaceV2)
[![Python Version](https://img.shields.io/pypi/pyversions/RecursiveNamespaceV2)](https://pypi.org/project/RecursiveNamespaceV2/)
[![PyPI version](https://badge.fury.io/py/RecursiveNamespaceV2.svg)](https://badge.fury.io/py/RecursiveNamespaceV2)
[![License](https://img.shields.io/github/license/pasxd245/RecursiveNamespaceV2)](https://github.com/pasxd245/RecursiveNamespaceV2/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Description

**RecursiveNamespace** is an extension of Python's **SimpleNamespace** that provides enhanced functionality for working with nested namespaces and dictionaries. This package allows easy access and manipulation of deeply nested data structures in an intuitive and Pythonic way.

## Installation

To install **RecursiveNamespaceV2** from PyPI use the following command.

```bash
pip install RecursiveNamespaceV2
```

If you want to use the github clone, use the following.

```bash
git clone https://github.com/pasxd245/RecursiveNamespaceV2.git
cd RecursiveNamespaceV2
python -m venv .venv  # to setup a virtual env.
pip install -r .\requirements.txt
```

## Usage

The **RecursiveNamespace** class can be used in the same way as Python's **SimpleNamespace** class, but in a recursive fashion. The **RecursiveNamespace** class can be instantiated with a dictionary or keyword arguments. The **RecursiveNamespace** class also provides a `to_dict()` method that returns a dictionary representation of the namespace.

### Basic Usage

One of the best use cases of this module is converting `dict` into a recursive namespace, and back to `dict`.
Another usage is to convert a dictionary to a recursive namespace.

```python
from recursivenamespace import RNS # or RecursiveNamespace

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
print(type(rn)) # <class 'recursivenamespace.main.recursivenamespace'>
print(rn)       # RNS(name=John, age=30, address=RNS(street=123 Main St, city=Anytown))
print(rn.name)  # John
print(rn.address.city) # Anytown
print(rn.friends[1])   # Tom, yes it does recognize iterables

# convert back to dictionary
data2 = rn.to_dict()
print(type(data2)) # <class 'dict'>
print(data2 == data) # True
print(data2['address']['city']) # Anytown
print(data2['friends'][1])      # Tom
```

You can use the key or namespace interchangeably

```python
print(rn.friends[1] is rn['friends'][1]) # True
```

You can also use it with YAML.

```python
import yaml
from recursivenamespace import RNS
datatext = """
name: John
age: 30
address:
    street: 123 Main St
    city: Anytown
friends:
    - Jane
    - Tom
"""
data = yaml.safe_load(datatext)
rn = RNS(data) 
print(rn) # RNS(name=John, age=30, address=RNS(street=123 Main St, city=Anytown))

# convert back to YAML
data_yaml = yaml.dump(rn.to_dict())
```

Let's see other use cases. You can make a nested rns.

```python
from recursivenamespace import RNS
results = RNS(
    params=rns(
        alpha=1.0,
        beta=2.0,
    ),
    metrics=rns(
        accuracy=98.79,
        f1=97.62
    )
)
```

Access elements as dictionary keys or namespace attributes.

```python
print(results.params.alpha is results.params['alpha'])             # True
print(results['metrics'].accuracy is  results.metrics['accuracy']) # True
```

Convert only the metrics to dictionary.

```python
metrics_dict = results.metrics.to_dict()
print(metrics_dict) # {'accuracy': 98.79, 'f1': 97.62}
```

Or convert all to a nested dictionary.

```python
from pprint import pprint
output_dict = results.to_dict()
pprint(output_dict)
# {'metrics': {'accuracy': 98.79, 'f1': 97.62},
# 'params':  {'alpha': 1.0, 'beta': 2.0}}
```

Flatten the dictionary using a separator for keys.

```python
flat_dict = results.to_dict(flatten_sep='_')
pprint(flat_dict)
# {'metrics_accuracy': 98.79,
#  'metrics_f1': 97.62,
#  'params_alpha': 1.0,
#  'params_beta': 2.0}
```

Add more fields on the fly.

```python
results.experiment_name = 'experiment_name'
results.params.dataset_version = 'dataset_version'
results.params.gamma = 0.35
```

The character '-' in a key will be converted to '_'

```python
results.params['some-key'] = 'some-value'
print(results.params.some_key)                                  # some-value
print(results.params['some-key'] is results.params.some_key)    # True
print(results.params['some-key'] is results.params['some_key']) # True
```

### JSON / TOML Serialization

Convert to and from JSON strings or files:

```python
from recursivenamespace import RNS

config = RNS({"app": {"name": "MyApp"}, "port": 8080})

# To JSON string
json_str = config.to_json(indent=2)

# From JSON string
loaded = RNS.from_json(json_str)
assert loaded.app.name == "MyApp"

# File I/O
config.save_json("config.json")
loaded = RNS.load_json("config.json")
```

TOML works the same way (Python 3.11+ or `pip install tomli`):

```python
toml_str = config.to_toml()
config.save_toml("config.toml")
loaded = RNS.load_toml("config.toml")
```

### Context Managers

Temporarily modify a namespace without affecting the original:

```python
config = RNS({"debug": False, "port": 8000})

# overlay: applies overrides, restores on exit
with config.overlay({"debug": True}):
    assert config.debug is True
assert config.debug is False

# temporary: yields a deep copy
with config.temporary() as tmp:
    tmp.port = 9999
assert config.port == 8000
```

### Chain-Key Access

Set and get deeply nested values with dot notation:

```python
ns = RNS({})
ns.val_set("server.host", "localhost")
ns.val_set("users[].#", "Alice")   # append to array
ns.val_set("users[].#", "Bob")

print(ns.val_get("server.host"))    # localhost
print(ns.val_get("users[].0"))      # Alice
print(ns.get_or_else("missing", "N/A"))  # N/A
```

## Examples

See the [examples/](examples/) directory for 15 runnable examples organized by difficulty (basic, intermediate, advanced, real-world).

## Testing

To run tests, navigate to the project's root directory and execute:

```bash
pytest -s
# or with coverage:
coverage run -m pytest
```

## Contributing

Contributions to the **RecursiveNamespace** project are welcome! Please ensure that any pull requests include tests covering new features or fixes. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
