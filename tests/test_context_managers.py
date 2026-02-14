"""Tests for temporary() and overlay() context managers."""

from __future__ import annotations

import pytest

from recursivenamespace import RNS


# ── temporary() ─────────────────────────────────────────────────


class TestTemporary:
    def test_basic(self):
        cfg = RNS({"a": 1, "b": 2})
        with cfg.temporary() as tmp:
            assert tmp.a == 1
            tmp.a = 99
            assert tmp.a == 99
        assert cfg.a == 1

    def test_nested_modification(self):
        cfg = RNS({"x": {"y": 10}})
        with cfg.temporary() as tmp:
            tmp.x.y = 999
            assert tmp.x.y == 999
        assert cfg.x.y == 10

    def test_add_new_keys(self):
        cfg = RNS({"a": 1})
        with cfg.temporary() as tmp:
            tmp["new_key"] = "hello"
            assert tmp.new_key == "hello"
        assert not hasattr(cfg, "new_key")

    def test_delete_keys(self):
        cfg = RNS({"a": 1, "b": 2})
        with cfg.temporary() as tmp:
            del tmp["a"]
            assert "a" not in tmp
        assert cfg.a == 1

    def test_exception_inside(self):
        cfg = RNS({"a": 1})
        with pytest.raises(ValueError, match="boom"):
            with cfg.temporary() as tmp:
                tmp.a = 99
                raise ValueError("boom")
        assert cfg.a == 1


# ── overlay() ───────────────────────────────────────────────────


class TestOverlay:
    def test_basic(self):
        cfg = RNS({"debug": False, "port": 8000})
        with cfg.overlay({"debug": True}):
            assert cfg.debug is True
            assert cfg.port == 8000
        assert cfg.debug is False

    def test_new_keys_removed_on_exit(self):
        cfg = RNS({"a": 1})
        with cfg.overlay({"temp": "val"}):
            assert cfg.temp == "val"
        assert not hasattr(cfg, "temp")

    def test_restore_on_exception(self):
        cfg = RNS({"a": 1})
        with pytest.raises(RuntimeError):
            with cfg.overlay({"a": 99, "extra": "x"}):
                assert cfg.a == 99
                raise RuntimeError("fail")
        assert cfg.a == 1
        assert not hasattr(cfg, "extra")

    def test_empty_overrides(self):
        cfg = RNS({"a": 1})
        with cfg.overlay({}):
            assert cfg.a == 1
        assert cfg.a == 1

    def test_nested_rns_override(self):
        cfg = RNS({"db": {"host": "localhost", "port": 5432}})
        override = RNS({"host": "remote", "port": 9999})
        with cfg.overlay({"db": override}):
            assert cfg.db.host == "remote"
            assert cfg.db.port == 9999
        assert cfg.db.host == "localhost"
        assert cfg.db.port == 5432

    def test_multiple_overrides(self):
        cfg = RNS({"a": 1, "b": 2, "c": 3})
        with cfg.overlay({"a": 10, "b": 20}):
            assert cfg.a == 10
            assert cfg.b == 20
            assert cfg.c == 3
        assert cfg.a == 1
        assert cfg.b == 2

    def test_nested_overlays(self):
        cfg = RNS({"x": 1})
        with cfg.overlay({"x": 10}):
            assert cfg.x == 10
            with cfg.overlay({"x": 100}):
                assert cfg.x == 100
            assert cfg.x == 10
        assert cfg.x == 1

    def test_overlay_yields_self(self):
        cfg = RNS({"a": 1})
        with cfg.overlay({"a": 2}) as ref:
            assert ref is cfg
            assert ref.a == 2

    def test_overlay_with_key_normalization(self):
        cfg = RNS({"my_key": "original"})
        with cfg.overlay({"my-key": "overridden"}):
            assert cfg.my_key == "overridden"
        assert cfg.my_key == "original"
