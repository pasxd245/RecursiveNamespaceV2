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

The library solves this by giving every method a second, collision-free
home: ``obj._``. Data with method-name keys is accepted (you'll see a
``FutureWarning`` reminding you that the matching method must be
called as ``obj._.<name>()``); only the ``_`` proxy itself is reserved
and raises ``KeyError`` if you try to use ``"_"`` as a data key.

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
  direct-call API. Direct method calls emit a ``DeprecationWarning``
  pointing to the proxy form. Data keys that collide with public method
  names are accepted with a ``FutureWarning`` (a louder category,
  visible under Python's default filter); only ``_`` itself raises.
* **Phase 2.** The warning is tightened (raised in stricter test
  configurations).
* **Phase 3 (next major release).** Direct method access is removed.
  The shadow warning goes away because there is no method left to
  shadow. Only ``_`` stays reserved.

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

Warning visibility (read this if you're integrating RNS)
--------------------------------------------------------

RNS emits two warning categories with intentionally different visibility:

* **Shadow events** — your data key collides with a method name
  (e.g. ``RNS({"items": "..."})``). Emitted as ``FutureWarning``.
  ``FutureWarning`` is shown under Python's **default** filter, so the
  collision surfaces in production logs the first time it happens —
  exactly the case where the in-memory object is now subtly broken
  (``obj.items`` is a string, ``obj.items()`` raises ``TypeError``)
  while the JSON output still looks correct.

* **Direct-call deprecation** — you called ``obj.to_dict()`` instead
  of ``obj._.to_dict()``. Emitted as ``DeprecationWarning``. Python's
  default filter suppresses ``DeprecationWarning`` raised outside
  ``__main__``, so these will be silent in normal application runs.
  To see them during migration, opt in:

  .. code-block:: bash

      # one-off
      PYTHONWARNINGS=default python app.py

      # in CI / tests
      pytest -W default

  Or, in a logging-based app, route ``warnings`` through your logger
  at startup so the filter no longer applies:

  .. code-block:: python

      import logging
      logging.captureWarnings(True)

The rationale for the split: a shadow event is caused by **end-user
data** flowing into RNS and silently breaks the in-memory object, so
it must be unmissable. A direct-call deprecation is a **developer**
choosing the legacy API, and migration is something the developer
opts into when they're ready — the standard Python convention.

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
