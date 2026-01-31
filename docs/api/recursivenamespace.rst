recursivenamespace Module
==========================

.. automodule:: recursivenamespace.main
   :members:
   :undoc-members:
   :show-inheritance:

Main Class
----------

.. autoclass:: recursivenamespace.main.recursivenamespace
   :members:
   :special-members: __init__, __getitem__, __setitem__, __delitem__, __contains__, __eq__, __repr__, __len__
   :undoc-members:
   :show-inheritance:

   Core Methods
   ~~~~~~~~~~~~

   .. automethod:: val_set
   .. automethod:: val_get
   .. automethod:: get_or_else
   .. automethod:: to_dict
   .. automethod:: update
   .. automethod:: items
   .. automethod:: keys
   .. automethod:: values
   .. automethod:: copy
   .. automethod:: deepcopy
   .. automethod:: pop
   .. automethod:: as_schema

Decorator
---------

.. autofunction:: recursivenamespace.main.rns

Exceptions
----------

.. autoclass:: recursivenamespace.main.SetChainKeyError
   :members:
   :show-inheritance:

.. autoclass:: recursivenamespace.main.GetChainKeyError
   :members:
   :show-inheritance:
