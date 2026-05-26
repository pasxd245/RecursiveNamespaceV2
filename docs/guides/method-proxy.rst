Method Proxy (``obj._``)
========================

User data often contains keys that collide with library method names —
``items``, ``keys``, ``values``, ``update``, ``to_dict``, ``copy``, and
so on. Letting such data silently shadow the method would break the
API. RecursiveNamespaceV2 solves this with a single reserved attribute:
``obj._``, which exposes every public method through a proxy.

Why
---

Without the proxy:

.. code-block:: python

    rn = RNS({"items": [1, 2, 3]})   # would shadow rn.items()
    rn.items()                        # TypeError: 'list' object is not callable

To prevent this corruption, RNS protects all public method names from
being used as data keys — but that means real-world JSON containing
``"items"`` cannot be loaded. The ``obj._`` proxy is the way out: it
gives every method a second, collision-free home so the protection on
method names can be removed in a future release.

Three equivalent call shapes
----------------------------

All three converge on the same implementation in ``_StaticImpl``:

.. code-block:: python

    rn = RNS({"name": "John", "address": {"city": "Anytown"}})

    # 1. Bound proxy — preferred. Same ergonomics as a regular method.
    rn._.to_dict()
    rn._.val_set("address.zip", "12345")

    # 2. Class-level static container — useful in tests and tooling.
    RNS._.to_dict(rn)
    RNS._.val_get(rn, "address.city")

    # 3. Legacy direct call — works, but emits DeprecationWarning.
    rn.to_dict()

Migration plan
--------------

The migration runs over three releases:

* **Phase 1 (this release).** ``obj._`` ships alongside the legacy
  direct-call API. Every direct call emits a ``DeprecationWarning``
  pointing to the proxy form. Method names remain protected from data
  shadowing.
* **Phase 2.** The warning is tightened (raised in stricter test
  configurations).
* **Phase 3 (next major release).** Direct method access is removed.
  Once removed, the names are no longer protected and user data may
  contain keys like ``"items"`` or ``"to_dict"``. Only ``_`` itself
  stays protected.

What lives where
----------------

* **Instance methods** (``to_dict``, ``items``, ``val_set``, ...) live
  in ``_StaticImpl`` and are reached via ``obj._`` or ``RNS._``.
* **Classmethod factories** (``from_json``, ``from_toml``,
  ``load_json``, ``load_toml``) stay on the class. There is no
  ``obj._.from_json(...)``; use ``RNS.from_json(...)``.
* **Dunders** (``__setitem__``, ``__len__``, ``__copy__``, ...) and
  private helpers (``_re``, ``_chain_set_array``, ...) stay on the
  class. They are not part of the public API.

Suppressing the warning during migration
----------------------------------------

While you migrate, you can silence the warning per-callsite:

.. code-block:: python

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter(
            "ignore",
            DeprecationWarning,
        )
        rn.to_dict()           # silent

Or globally in your test config (``pyproject.toml``):

.. code-block:: toml

    [tool.pytest.ini_options]
    filterwarnings = [
        "ignore:Calling .* directly on an RNS instance is deprecated:DeprecationWarning",
    ]

Caveats
-------

* **Subclass overrides** of public methods are honoured by the legacy
  direct call but **not** by ``_StaticImpl.method(obj)`` — the static
  dispatcher always runs the base implementation. Prefer overriding the
  shim and calling through the proxy in Phase 1; full subclass support
  will arrive when direct methods are removed.
* **Type checkers** see ``obj._`` as ``Any`` because ``_BoundProxy``
  uses ``__getattr__``. IDE autocomplete still works via
  ``dir(obj._)``; full static typing arrives in a follow-up.
* ``obj._ is RNS._`` is **false**: class access returns the static
  container, instance access returns a fresh bound proxy.
