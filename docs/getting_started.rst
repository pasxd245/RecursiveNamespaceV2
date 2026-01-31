Getting Started
===============

Installation
------------

From PyPI::

    pip install RecursiveNamespaceV2

From Source::

    git clone https://github.com/pasxd245/RecursiveNamespaceV2.git
    cd RecursiveNamespaceV2
    pip install -e .

Basic Usage
-----------

Creating a Recursive Namespace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from recursivenamespace import RNS

    # From a dictionary
    data = {'name': 'John', 'age': 30}
    rn = RNS(data)

    # From keyword arguments
    rn = RNS(name='John', age=30)

    # Access values
    print(rn.name)  # John
    print(rn['age'])  # 30

Nested Structures
~~~~~~~~~~~~~~~~~

.. code-block:: python

    data = {
        'user': {
            'profile': {
                'name': 'John',
                'email': 'john@example.com'
            }
        }
    }

    rn = RNS(data)
    print(rn.user.profile.name)  # John

Converting Back to Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    rn = RNS({'a': {'b': {'c': 1}}})

    # Regular dict
    d = rn.to_dict()

    # Flattened dict
    flat_d = rn.to_dict(flatten_sep='_')
    # {'a_b_c': 1}

Key Normalization
~~~~~~~~~~~~~~~~~

By default, hyphens and spaces are converted to underscores:

.. code-block:: python

    rn = RNS({'some-key': 'value'})
    print(rn.some_key)  # value
    print(rn['some-key'])  # value (both work)

To preserve original keys:

.. code-block:: python

    rn = RNS(data, use_raw_key=True)
