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

The **RecursiveNamespace** class can be used in the same way as Python's **SimpleNamespace** class, but in a recursive fashion. The **RecursiveNamespace** class can be instantiated with a dictionary or keyword arguments. The **RecursiveNamespace** class also provides a `to_dict()` method that returns a dictionary representation of the namespace.

I prefer to use the class as the following

```python
results = RN(
    params=RN(
        alpha=1.0,
        beta=2.0,
        dataset_name='dataset_name',
        dataset_path='dataset_path',
        classifier_name='classifier_name',
    ),
    metrics=RN(
        accuracy=98.79,
        f1=97.62
    )
)

print(results.params.k1) # 1.0
print(results.metrics.accuracy) # 98.79
```

Then I can add more information on the fly.

```python
results.experiment_name = 'experiment_name'
results.params.dataset_version = 'dataset_version'
results.params.gamma = 0.35
print(results.params.gamma) # 0.35
```

Then I'd convert it to nested or flattened dictionary.
  
```python
output_dict = results.to_dict()
output_dict_flat = results.to_dict(flatten_sep='_')  # flattened dictionary
```
Or just convert metrics to dictionary.

```python
metrics_dict = results.metrics.to_dict()
```

Another usage would be to convert a dictionary to a recursive namespace.

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