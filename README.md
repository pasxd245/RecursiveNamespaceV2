# RecursiveNamespace

## Description
**RecursiveNamespace** is an extension of Python's **SimpleNamespace** that provides enhanced functionality for working with nested namespaces and dictionaries. This package allows easy access and manipulation of deeply nested data structures in an intuitive and Pythonic way.

## Installation
To install **RecursiveNamespace**, simply clone the repository and install using pip:

```bash
git clone https://github.com/HessamLa/RecursiveNamespace.git
cd RecursiveNamespace
pip install .
```

# Usage
## Basic Usage
The `basic_usage.py` example demonstrates how to create a simple recursive namespace:

```python
from pprint import pprint
from RecursiveNamespace import RecursiveNamespace

# Creating a simple recursive namespace
data = {
    'name': 'John Doe',
    'age': 30,
    'address': {
        'street': '123 Main St',
        'city': 'Anytown'
    }
}

rn = RecursiveNamespace(data)
print(rn) #RN(name=John Doe, age=30, address=RN(street=123 Main St, city=Anytown))

print(rn.name) # John Doe
print(rn.address.street) # 123 Main St

print(rn.to_dict()) # {'name': 'John Doe', 'age': 30, 'address': {'street': '123 Main St', 'city': 'Anytown'}}

pprint(rn.to_dict(flatten_sep='_')) 
# {'name': 'John Doe', 'age': 30, 'address_street': '123 Main St', 'address_city': 'Anytown'}


rn.scores = RecursiveNamespace({'score-1': 98.4, 'score-2': 100})
print(rn.scores.score_1) # 98.4
print(rn.scores.score_2) # 100
rn.scores.score_3 = 99.07
print(rn.scores.score_3) # 99.07
```

# Testing
To run tests, navigate to the project's root directory and execute:

```bash
python -m unittest discover tests
```
The `test_recursive_namespace.py` file contains tests for the **RecursiveNamespace** class.

# Contributing
Contributions to the **RecursiveNamespace** project are welcome! Please ensure that any pull requests include tests covering new features or fixes.

# License
This project is licensed under the MIT License - see the `LICENSE` file for details.

You should copy the actual content from examlpes scripts (founde under `./examples/` directory) and paste it into the respective sections of the README. This provides users with immediate examples of how to use your package. The Testing section explains how to run the unit tests, encouraging users to check that everything is working correctly.