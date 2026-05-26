Getting Started
===============

Installation
------------

From PyPI::

    pip install RecursiveNamespaceV2
    # or with uv
    uv pip install RecursiveNamespaceV2

From Source (using uv)::

    git clone https://github.com/pasxd245/RecursiveNamespaceV2.git
    cd RecursiveNamespaceV2
    uv venv
    uv pip install -e ".[test]"

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

Public methods live under the ``obj._`` proxy. Calling them directly on
the instance (e.g. ``rn.to_dict()``) still works in Phase 1 of the
migration but emits a ``DeprecationWarning`` — prefer the proxy form:

.. code-block:: python

    rn = RNS({'a': {'b': {'c': 1}}})

    # Regular dict
    d = rn._.to_dict()

    # Flattened dict
    flat_d = rn._.to_dict(flatten_sep='_')
    # {'a_b_c': 1}

See :doc:`guides/method-proxy` for the full migration story.

Key Normalization
~~~~~~~~~~~~~~~~~

By default, hyphens, dots, and whitespace are converted to underscores
so the value is reachable as both an attribute and an item:

.. code-block:: python

    rn = RNS({'some-key': 'value'})
    print(rn.some_key)  # value
    print(rn['some-key'])  # value (both work)

To preserve original keys (no normalization):

.. code-block:: python

    rn = RNS(data, use_raw_key=True)

Reserved and Protected Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two tiers of names are reserved on the class:

* **Hard-protected** — every single-underscore attribute on ``RNS``
  (the ``_`` method proxy plus internal helpers like ``_re_``,
  ``_process_``, ``_chain_*_``, ``_logger_``). Using one of these as a
  data key raises ``KeyError``.
* **Soft-protected (deprecated public methods)** — names like
  ``to_dict``, ``val_set``, ``val_get``, ``update``, ``keys``,
  ``values``, ``items``, ``copy``, ``deepcopy``, ``pop``, ``as_schema``,
  ``to_json``/``from_json``, ``to_toml``/``from_toml``, etc. Storing a
  data field with one of these names is allowed but emits a
  ``DeprecationWarning``: ``obj[name]`` / ``obj.name`` will return the
  data, and the method remains reachable via ``obj._.<name>(...)``.

Classmethod Factories
~~~~~~~~~~~~~~~~~~~~~

Deserializers are **classmethods**, not instance methods — call them on
``RNS`` directly, not through the ``_`` proxy:

.. code-block:: python

    rn = RNS.from_json('{"a": 1, "b": {"c": 2}}')
    rn = RNS.load_json('config.json')
    rn = RNS.from_toml('a = 1\nb.c = 2')
    rn = RNS.load_toml('config.toml')

Round-trip with the instance serializers:

.. code-block:: python

    rn = RNS(a=1, b={'c': 2})
    text = rn._.to_json()
    rn._.save_json('out.json')
    same = RNS.from_json(text)
