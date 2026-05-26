"""Tests targeting uncovered code paths in main.py.

Covers: key management, update, equality, len, deletion,
contains, protected keys, copy/deepcopy, pop, values, chain-key
errors, array errors, get_or_else, as_schema, and rns decorator.
"""

from __future__ import annotations

import dataclasses
import warnings

import pytest

from recursivenamespace import RNS, rns
from recursivenamespace.main import (
    GetChainKeyError,
    SetChainKeyError,
    recursivenamespace,
)
from recursivenamespace.utils import KV_Pair


# ── Key management ──────────────────────────────────────────────


class TestKeyManagement:
    def test_set_get_key(self):
        ns = RNS({"a": 1})
        ns.set_key("mykey")
        assert ns.get_key() == "mykey"


# ── Update ──────────────────────────────────────────────────────


class TestUpdate:
    def test_update_with_dict(self):
        ns = RNS({"a": 1})
        ns.update({"b": 2, "c": 3})
        assert ns.b == 2
        assert ns.c == 3

    def test_update_with_rns(self):
        ns = RNS({"a": 1})
        ns.update(RNS({"b": 2}))
        assert ns.b == 2
        assert ns.a == 1


# ── Equality ────────────────────────────────────────────────────


class TestEquality:
    def test_eq_with_dict(self):
        ns = RNS({"a": 1})
        # vars(ns) includes protected keys, so a plain
        # dict without them should NOT equal the namespace.
        assert ns != {"a": 1}

    def test_eq_non_matching_type(self):
        ns = RNS({"a": 1})
        assert ns != 42
        assert ns != "string"
        assert ns != [1, 2]


# ── Length ──────────────────────────────────────────────────────


class TestLen:
    def test_len(self):
        ns = RNS({"a": 1, "b": 2, "c": 3})
        assert len(ns) == 3

    def test_len_empty(self):
        ns = RNS({})
        assert len(ns) == 0


# ── Deletion ────────────────────────────────────────────────────


class TestDeletion:
    def test_delattr(self):
        ns = RNS({"a": 1, "b": 2})
        del ns.a
        assert not hasattr(ns, "a")
        assert len(ns) == 1

    def test_delitem(self):
        ns = RNS({"a": 1, "b": 2})
        del ns["a"]
        assert "a" not in ns
        assert len(ns) == 1


# ── Contains ────────────────────────────────────────────────────


class TestContains:
    def test_contains(self):
        ns = RNS({"a": 1})
        assert "a" in ns
        assert "b" not in ns


# ── Protected keys ──────────────────────────────────────────────


class TestProtectedKeys:
    def test_setitem_protected(self):
        ns = RNS({"a": 1})
        with pytest.raises(KeyError, match="protected"):
            ns["_key_"] = "bad"

    def test_getitem_protected(self):
        ns = RNS({"a": 1})
        with pytest.raises(KeyError, match="protected"):
            _ = ns["_key_"]

    def test_pop_protected(self):
        ns = RNS({"a": 1})
        with pytest.raises(KeyError, match="protected"):
            ns.pop("_key_")

    @pytest.mark.parametrize(
        "name",
        [
            "to_dict",
            "items",
            "keys",
            "values",
            "update",
            "pop",
            "copy",
            "deepcopy",
            "val_set",
            "val_get",
            "get_or_else",
            "set_key",
            "get_key",
            "as_schema",
            "to_json",
            "from_json",
            "to_toml",
            "from_toml",
            "temporary",
            "overlay",
        ],
    )
    def test_init_data_collides_with_method_warns_and_accepts(self, name):
        # Method names are soft-protected: data is accepted, a
        # FutureWarning tells the caller to use obj._.<name>() for
        # the method. FutureWarning (not DeprecationWarning) so it's
        # visible under Python's default warning filter.
        with pytest.warns(FutureWarning, match="shadows"):
            ns = RNS({name: "x"})
        assert ns[name] == "x"

    def test_init_kwargs_collides_with_method_warns_and_accepts(self):
        with pytest.warns(FutureWarning, match="shadows"):
            ns = RNS(items=[1, 2, 3])
        assert ns["items"] == [1, 2, 3]

    def test_setitem_method_name_warns_and_accepts(self):
        ns = RNS({"a": 1})
        with pytest.warns(FutureWarning, match="shadows"):
            ns["to_dict"] = "shadowed"
        assert ns["to_dict"] == "shadowed"

    def test_val_set_method_name_warns_and_accepts(self):
        ns = RNS({"a": 1})
        with pytest.warns(FutureWarning, match="shadows"):
            ns._.val_set("update", "shadowed")
        assert ns["update"] == "shadowed"

    def test_methods_remain_callable_after_normal_init(self):
        # Sanity: the protection must not break ordinary usage.
        ns = RNS({"a": 1, "b": {"c": 2}})
        assert ns._.to_dict() == {"a": 1, "b": {"c": 2}}
        assert ns._.keys() == ["a", "b"]
        assert "a" in dict(ns._.items())

    def test_nested_dict_method_collision_also_warns(self):
        # Nested dicts are recursively wrapped, so the warning fires
        # for the inner shadowing too.
        with pytest.warns(FutureWarning, match="shadows"):
            ns = RNS({"outer": {"to_dict": "x"}})
        assert ns.outer["to_dict"] == "x"

    def test_underscore_helpers_still_hard_protected(self):
        # Single-underscore helpers (and the state attrs) stay strict
        # — shadowing them would break internal logic.
        with pytest.raises(KeyError, match="protected"):
            RNS({"_re_": "bad"})
        with pytest.raises(KeyError, match="protected"):
            RNS({"_chain_set_array_": "bad"})

    def test_proxy_sees_shadowed_data_via_items(self):
        # After shadowing, obj._.items() should include the shadowing
        # entry alongside the rest of the data.
        with pytest.warns(FutureWarning, match="shadows"):
            ns = RNS({"a": 1, "items": [1, 2, 3]})
        d = ns._.to_dict()
        assert d == {"a": 1, "items": [1, 2, 3]}


# ── Copy / Deepcopy ────────────────────────────────────────────


class TestCopy:
    def test_shallow_copy(self):
        ns = RNS({"a": 1, "b": {"c": 2}})
        c = ns.copy()
        assert c.a == 1
        assert c.b.c == 2

    def test_deepcopy_independence(self):
        ns = RNS({"a": 1, "b": {"c": 2}})
        dc = ns.deepcopy()
        dc.b.c = 99
        assert ns.b.c == 2


# ── Pop ─────────────────────────────────────────────────────────


class TestPop:
    def test_pop_existing(self):
        ns = RNS({"a": 1, "b": 2})
        val = ns.pop("a")
        assert val == 1
        assert "a" not in ns

    def test_pop_missing_with_default(self):
        ns = RNS({"a": 1})
        val = ns.pop("z", "default")
        assert val == "default"


# ── Values ──────────────────────────────────────────────────────


class TestValues:
    def test_values(self):
        ns = RNS({"a": 1, "b": 2})
        vals = ns.values()
        assert 1 in vals
        assert 2 in vals


# ── Iterator ────────────────────────────────────────────────────


class TestIterator:
    def test_iter_keys(self):
        ns = RNS({"a": 1, "b": 2})
        assert sorted(ns) == ["a", "b"]

    def test_dict_conversion_via_iter(self):
        ns = RNS({"x": 10})
        d = dict(ns)
        assert d == {"x": 10}


# ── Chain-key set errors ────────────────────────────────────────


class TestChainSetErrors:
    def test_set_chain_key_on_non_rns(self):
        ns = RNS({"a": "not_an_rns"})
        with pytest.raises(SetChainKeyError):
            ns.val_set("a.b", 1)

    def test_set_array_on_non_list(self):
        ns = RNS({"a": "string"})
        with pytest.raises(KeyError, match="Invalid array key"):
            ns.val_set("a[].0", 1)

    def test_set_array_no_index(self):
        ns = RNS({"a": [1, 2, 3]})
        with pytest.raises(KeyError, match="Required the 'index'"):
            ns.val_set("a[]", 1)

    def test_set_chain_on_non_rns_array_element(self):
        ns = RNS({"a": ["plain_string"]})
        with pytest.raises(SetChainKeyError):
            ns.val_set("a[].0.sub_key", 1)


# ── Chain-key get errors ────────────────────────────────────────


class TestChainGetErrors:
    def test_get_chain_key_on_non_rns(self):
        ns = RNS({"a": "not_an_rns"})
        with pytest.raises(GetChainKeyError):
            ns.val_get("a.b.c")

    def test_get_array_on_non_list(self):
        ns = RNS({"a": "string"})
        with pytest.raises(KeyError, match="Invalid array key"):
            ns.val_get("a[].0")

    def test_get_array_no_index(self):
        ns = RNS({"a": [1, 2, 3]})
        with pytest.raises(KeyError, match="Required the 'index'"):
            ns.val_get("a[]")

    def test_get_chain_on_non_rns_deep(self):
        ns = RNS({"a": ["plain_string"]})
        with pytest.raises(GetChainKeyError):
            ns.val_get("a[].0.x.y")


# ── get_or_else ─────────────────────────────────────────────────


class TestGetOrElse:
    def test_missing_key_returns_default(self):
        ns = RNS({"a": 1})
        assert ns.get_or_else("missing") is None
        assert ns.get_or_else("missing", 42) == 42

    def test_show_log(self):
        ns = RNS({"a": 1})
        result = ns.get_or_else("missing", "fb", show_log=True)
        assert result == "fb"


# ── as_schema ───────────────────────────────────────────────────


class TestAsSchema:
    def test_non_dataclass_raises(self):
        ns = RNS({"a": 1})
        with pytest.raises(TypeError, match="DataClass"):
            ns.as_schema(dict)


# ── rns decorator ───────────────────────────────────────────────


class TestRnsDecorator:
    def test_accepted_iter_types(self):
        @rns.rns(accepted_iter_types=[tuple])
        def create():
            return {"data": (1, 2, 3)}

        result = create()
        assert isinstance(result, recursivenamespace)
        assert result.data == (1, 2, 3)

    def test_chain_key_with_kv_pairs(self):
        @rns.rns(use_chain_key=True)
        def create():
            return [
                KV_Pair("a.b", 1),
                KV_Pair("c", 2),
            ]

        result = create()
        assert result.a.b == 1
        assert result.c == 2

    def test_non_dict_return(self):
        @rns.rns()
        def create():
            return "just a string"

        result = create()
        assert result.props == "just a string"

    def test_dataclass_return(self):
        @dataclasses.dataclass
        class Config:
            x: int = 1
            y: str = "hello"

        @rns.rns()
        def create():
            return Config(x=10, y="world")

        result = create()
        assert result.x == 10
        assert result.y == "world"

    def test_dict_return_with_method_collision_warns(self):
        @rns.rns()
        def create():
            return {"to_dict": "x", "name": "foo"}

        with pytest.warns(FutureWarning, match="shadows"):
            result = create()
        assert result["to_dict"] == "x"
        assert result.name == "foo"

    def test_non_dict_return_with_props_collision_warns(self):
        @rns.rns(props="items")
        def create():
            return [1, 2, 3]

        with pytest.warns(FutureWarning, match="shadows"):
            result = create()
        assert result["items"] == [1, 2, 3]

    def test_chain_key_dict_return_collision_warns(self):
        @rns.rns(use_chain_key=True)
        def create():
            return {"to_dict": "x"}

        with pytest.warns(FutureWarning, match="shadows"):
            result = create()
        assert result["to_dict"] == "x"

    def test_dataclass_field_collision_warns(self):
        @dataclasses.dataclass
        class Bad:
            items: list = dataclasses.field(default_factory=list)
            name: str = "foo"

        @rns.rns()
        def create():
            return Bad(items=[1, 2, 3], name="foo")

        with pytest.warns(FutureWarning, match="shadows"):
            result = create()
        assert result["items"] == [1, 2, 3]


# ── Serialization error paths ───────────────────────────────────


class TestSerializationErrors:
    def test_to_toml_none_value(self):
        ns = RNS({"a": None, "b": 1})
        toml_str = ns.to_toml()
        assert "b = 1" in toml_str

    def test_to_toml_complex_array(self):
        ns = RNS({"a": [{"nested": 1}]})
        toml_str = ns.to_toml()
        assert "complex array" in toml_str

    def test_to_toml_unsupported_type(self):
        ns = RNS({})
        # Bypass __setitem__ to inject a non-standard type
        ns.__dict__["custom"] = object()
        toml_str = ns.to_toml()
        assert "not supported" in toml_str


# ── Method proxy (obj._.method) ─────────────────────────────────


class TestMethodProxy:
    """Phase 1 of the method-proxy migration.

    Public methods are reachable via three equivalent shapes:
      - ``obj._.method(...)``     — bound proxy (preferred)
      - ``RNS._.method(obj, ...)`` — class-level static container
      - ``obj.method(...)``       — legacy, emits DeprecationWarning
    All three converge on ``_StaticImpl.method``.
    """

    # ---- ``obj._`` returns a fresh bound proxy ----

    def test_obj_underscore_parity_with_direct_call(self):
        ns = RNS({"a": 1, "b": {"c": 2}})
        # ``ns.to_dict()`` warns; the proxy form is silent.
        assert ns._.to_dict() == {"a": 1, "b": {"c": 2}}
        assert ns._.keys() == ["a", "b"]
        assert ns._.values() == [1, ns.b]

    def test_proxy_val_get_chain_key(self):
        ns = RNS({"a": {"b": {"c": 42}}})
        assert ns._.val_get("a.b.c") == 42

    def test_proxy_val_set_chain_key(self):
        ns = RNS({})
        ns._.val_set("a.b.c", 7)
        assert ns._.val_get("a.b.c") == 7

    def test_proxy_repr_is_sensible(self):
        ns = RNS({"a": 1})
        assert "RNS method proxy" in repr(ns._)

    def test_proxy_dir_lists_public_methods(self):
        ns = RNS({"a": 1})
        names = set(dir(ns._))
        # Some representative public methods must be discoverable.
        for n in (
            "to_dict",
            "items",
            "keys",
            "values",
            "val_get",
            "val_set",
            "update",
            "copy",
            "deepcopy",
        ):
            assert n in names
        # No dunders / privates leak through.
        for n in names:
            assert not n.startswith("_")

    # ---- ``RNS._`` (class access) returns the static container ----

    def test_class_underscore_returns_static_impl(self):
        ns = RNS({"a": 1, "b": 2})
        from recursivenamespace.main import _StaticImpl

        assert RNS._ is _StaticImpl
        assert RNS._.to_dict(ns) == {"a": 1, "b": 2}
        assert RNS._.items(ns) == [("a", 1), ("b", 2)]

    # ---- ``_`` itself is protected from user-data shadowing ----

    def test_init_data_collides_with_underscore_protected(self):
        with pytest.raises(KeyError, match="protected"):
            RNS({"_": "bad"})

    def test_setitem_underscore_protected(self):
        ns = RNS({"a": 1})
        with pytest.raises(KeyError, match="protected"):
            ns["_"] = "bad"

    def test_val_set_underscore_protected(self):
        ns = RNS({"a": 1})
        with pytest.raises(KeyError, match="protected"):
            ns._.val_set("_", "bad")

    def test_underscore_assignment_blocked_by_data_descriptor(self):
        ns = RNS({"a": 1})
        with pytest.raises(AttributeError, match="reserved"):
            ns._ = "bad"

    def test_underscore_deletion_blocked_by_data_descriptor(self):
        ns = RNS({"a": 1})
        with pytest.raises(AttributeError, match="reserved"):
            del ns._

    def test_proxy_setattr_read_only(self):
        ns = RNS({"a": 1})
        with pytest.raises(AttributeError, match="read-only"):
            ns._.something = "bad"

    # ---- ``_`` is not data ----

    def test_underscore_not_in_to_dict(self):
        ns = RNS({"a": 1})
        assert "_" not in ns._.to_dict()

    def test_underscore_not_in_keys(self):
        ns = RNS({"a": 1})
        assert "_" not in ns._.keys()

    def test_underscore_not_in_contains(self):
        ns = RNS({"a": 1})
        assert "_" not in ns

    # ---- Deprecation warning ----

    def test_direct_call_emits_deprecation(self):
        ns = RNS({"a": 1})
        with pytest.warns(DeprecationWarning, match="to_dict.*deprecated"):
            ns.to_dict()

    def test_proxy_call_does_not_emit_deprecation(self):
        ns = RNS({"a": 1})
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            # Must not raise — proxy path is the new recommended form.
            assert ns._.to_dict() == {"a": 1}

    def test_static_call_does_not_emit_deprecation(self):
        ns = RNS({"a": 1})
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            assert RNS._.to_dict(ns) == {"a": 1}

    # ---- Pickle, copy, nested behavior ----

    def test_pickle_roundtrip_proxy_still_works(self):
        import pickle

        ns = RNS({"a": 1, "b": {"c": 2}})
        loaded = pickle.loads(pickle.dumps(ns))
        assert loaded._.to_dict() == {"a": 1, "b": {"c": 2}}

    def test_nested_rns_has_own_proxy(self):
        ns = RNS({"outer": {"inner": 1}})
        assert ns.outer._.to_dict() == {"inner": 1}
        # Each access yields a fresh proxy bound to its owner.
        assert ns._ is not ns.outer._

    def test_classmethod_factories_not_on_proxy(self):
        # Factories live on the class (RNS.from_json), not on the
        # instance proxy — they create instances, they don't act on one.
        ns = RNS({"a": 1})
        with pytest.raises(AttributeError):
            _ = ns._.from_json

    def test_internal_recursion_does_not_emit_deprecation(self):
        # to_dict recurses on nested RNS values; the recursion goes
        # through _StaticImpl directly so no warning should fire.
        ns = RNS({"a": {"b": {"c": 1}}})
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            assert ns._.to_dict() == {"a": {"b": {"c": 1}}}
