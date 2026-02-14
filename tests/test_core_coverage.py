"""Tests targeting uncovered code paths in main.py.

Covers: key management, update, equality, len, deletion,
contains, protected keys, copy/deepcopy, pop, values, chain-key
errors, array errors, get_or_else, as_schema, and rns decorator.
"""

from __future__ import annotations

import dataclasses

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
            ns["_recursivenamespace__key_"] = "bad"

    def test_getitem_protected(self):
        ns = RNS({"a": 1})
        with pytest.raises(KeyError, match="protected"):
            _ = ns["_recursivenamespace__key_"]

    def test_pop_protected(self):
        ns = RNS({"a": 1})
        with pytest.raises(KeyError, match="protected"):
            ns.pop("_recursivenamespace__key_")


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
