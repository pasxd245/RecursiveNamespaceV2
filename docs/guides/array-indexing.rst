Array Indexing
==============

RecursiveNamespace provides special syntax for working with arrays.

Basic Array Access
------------------

.. code-block:: python

    from recursivenamespace import RNS

    rn = RNS({
        'items': [
            {'name': 'Item 1'},
            {'name': 'Item 2'},
            {'name': 'Item 3'}
        ]
    })

    # Access by index
    rn.val_set('items[].0.name', 'Updated Item 1')

    # Access last item
    rn.val_set('items[].-1.name', 'Last Item')

Appending to Arrays
-------------------

Use the ``#`` symbol to append:

.. code-block:: python

    # Append a new item
    rn.val_set('items[].#', {'name': 'New Item'})

    # Append with nested values
    rn.val_set('items[].#.name', 'Another Item')

Nested Arrays
-------------

.. code-block:: python

    rn = RNS({
        'matrix': [
            [1, 2, 3],
            [4, 5, 6]
        ]
    })

    # Access nested array element
    value = rn.val_get('matrix[].0[].1')  # 2

    # Modify nested array
    rn.val_set('matrix[].1[].0', 10)  # matrix[1][0] = 10

Complex Example
---------------

.. code-block:: python

    # Create nested structure with arrays
    rn = RNS()
    rn.val_set('users[].#.name', 'Alice')
    rn.val_set('users[].-1.emails[].#', 'alice@example.com')
    rn.val_set('users[].-1.emails[].#', 'alice2@example.com')

    # Result:
    # {
    #   'users': [
    #     {
    #       'name': 'Alice',
    #       'emails': ['alice@example.com', 'alice2@example.com']
    #     }
    #   ]
    # }
