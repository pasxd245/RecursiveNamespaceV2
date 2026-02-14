RecursiveNamespaceV2 Documentation
===================================

**RecursiveNamespaceV2** is a Python library that extends Python's built-in ``SimpleNamespace``
class to provide enhanced functionality for working with nested namespaces and dictionaries.

Features
--------

* **Automatic Recursive Conversion**: Converts nested dictionaries to namespaces automatically
* **Dual Access Pattern**: Access elements using both dictionary keys and namespace attributes
* **Chain-Key Access**: Advanced key access using dot notation (e.g., ``rns.val_get("a.b.c")``)
* **Array Indexing**: Special syntax for arrays (``key[].#`` for append, ``key[].0`` for index access)
* **Type-Safe**: Fully typed with mypy support
* **Zero Dependencies**: Pure Python implementation
* **Flexible Serialization**: Easy conversion between dict and namespace

Quick Start
-----------

Installation::

    pip install RecursiveNamespaceV2
    # or with uv
    uv pip install RecursiveNamespaceV2

Basic Usage:

.. code-block:: python

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

    # Convert back to dict
    data_dict = rn.to_dict()

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting_started
   guides/chain-keys
   guides/array-indexing

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/recursivenamespace
   api/utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
