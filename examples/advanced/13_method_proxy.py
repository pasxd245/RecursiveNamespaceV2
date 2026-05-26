"""Method proxy (``obj._``): the migration path for method-name collisions.

User data frequently contains keys like ``"items"``, ``"keys"``,
``"update"`` — names that would otherwise shadow library methods.
RecursiveNamespaceV2 protects those names and gives you a single
collision-free way to call methods: ``obj._.method(...)``.
"""

import warnings

from recursivenamespace import RNS

# ── 1. Collision case ────────────────────────────────────────────
# Method names are SOFT-protected: data is accepted, a
# FutureWarning tells you the matching method must be called via
# obj._.<name>(). FutureWarning (not DeprecationWarning) so the
# collision is visible under Python's default warning filter — the
# in-memory object is now broken (collision.items is the list, not the
# method), and that should not require -W default to notice.

with warnings.catch_warnings(record=True) as captured:
    warnings.simplefilter("always", FutureWarning)
    collision = RNS({"items": [1, 2, 3], "name": "John"})
    print(f"Stored data: items={collision['items']}, name={collision.name}")
    print(f"Shadow warning: {captured[0].message}")

# ── 2. The proxy as the new access form ──────────────────────────
# ``obj._.method()`` works without any deprecation warning.

rn = RNS({"name": "John", "address": {"city": "Anytown"}})

print(f"\nrn._.to_dict() = {rn._.to_dict()}")
print(f"rn._.keys()    = {rn._.keys()}")

rn._.val_set("address.zip", "12345")
print(f"rn._.val_get('address.zip') = {rn._.val_get('address.zip')}")

# ── 3. Class-level static container ──────────────────────────────
# ``RNS._`` returns the implementation container directly. Useful in
# tests and tooling where you want to pass the RNS instance explicitly.

print(f"\nRNS._.to_dict(rn) = {RNS._.to_dict(rn)}")
print(f"RNS._.items(rn)   = {RNS._.items(rn)}")

# ── 4. Legacy direct call still works, but warns ─────────────────
# Existing code keeps running while you migrate.

with warnings.catch_warnings(record=True) as captured:
    warnings.simplefilter("always", DeprecationWarning)
    _ = rn.to_dict()
    assert any("to_dict" in str(w.message) for w in captured), (
        "expected DeprecationWarning"
    )
    print(f"\nLegacy rn.to_dict() emitted: {captured[-1].message}")

# ── 5. Factories live on the class (no migration needed) ─────────
# from_json / from_toml / load_json / load_toml create instances —
# they have nothing to do with ``obj._``. Call them on the class.

rn2 = RNS.from_json('{"a": 1, "b": {"c": 2}}')
print(f"\nRNS.from_json(...) -> {rn2._.to_dict()}")

# ── 6. ``_`` is the one hard-reserved name ───────────────────────
# It backs the proxy itself, so it stays strictly protected.

try:
    RNS({"_": "bad"})
except KeyError as exc:
    print(f"\nUser data cannot use '_': {exc}")

try:
    rn._ = "bad"
except AttributeError as exc:
    print(f"Cannot reassign rn._: {exc}")
