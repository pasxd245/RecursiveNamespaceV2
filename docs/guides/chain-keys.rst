Chain-Key Access
================

Chain-keys allow you to access deeply nested values using dot notation.

Basic Chain-Key Access
-----------------------

.. code-block:: python

    from recursivenamespace import RNS

    rn = RNS({
        'level1': {
            'level2': {
                'level3': 'value'
            }
        }
    })

    # Set using chain-key
    rn.val_set('level1.level2.level3', 'new value')

    # Get using chain-key
    value = rn.val_get('level1.level2.level3')  # 'new value'

Safe Access
-----------

Use ``get_or_else`` for safe access with defaults:

.. code-block:: python

    # Returns default if key doesn't exist
    value = rn.get_or_else('nonexistent.key', default='fallback')

Escaping Special Characters
----------------------------

If your keys contain dots, escape them:

.. code-block:: python

    # Key contains a literal dot
    rn.val_set(r'key\\.with\\.dots', 'value')
    value = rn.val_get(r'key\\.with\\.dots')

Performance Tips
----------------

* Chain-key access is slightly slower than direct access
* For frequently accessed paths, consider caching the reference
* Use direct attribute access when possible: ``rn.a.b.c`` instead of ``rn.val_get('a.b.c')``
