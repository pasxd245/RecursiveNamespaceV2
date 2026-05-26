#############################
# Fork: https://github.com/HessamLa/recursivenamespace
# %%
from __future__ import annotations

import contextlib
import dataclasses
import functools
import json
import logging
import re
import sys
import warnings
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union,
)

# Conditional import for TOML support
try:
    import tomllib  # type: ignore[import-not-found]  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[import-not-found]
    except ImportError:
        tomllib = None

from . import utils
from .errors import GetChainKeyError, SerializationError, SetChainKeyError

T = TypeVar("T")

_KEY_NORMALIZE_RE = re.compile(r"[.\-\s]")

__all__ = [
    "recursivenamespace",
    "GetChainKeyError",
    "SerializationError",
    "SetChainKeyError",
]


# Phase 1 of the method-proxy migration: public methods will eventually
# live exclusively under ``obj._.<method>(...)``. For now the class still
# exposes them directly as shims that warn and delegate to _StaticImpl,
# the single source of truth.
_DEPRECATION_TEMPLATE = (
    "Calling '{name}' directly on an RNS instance is deprecated and "
    "will be removed in a future major release. Use 'obj._.{name}(...)' "
    "instead."
)


def _deprecated(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a class-level shim as deprecated in favor of ``obj._.method(...)``.

    Emits DeprecationWarning at call time using the wrapped function's
    name, then forwards. Remove these decorators (and the shims they
    decorate) in Phase 3 of the migration.
    """
    msg = _DEPRECATION_TEMPLATE.format(name=func.__name__)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    return wrapper


class recursivenamespace(SimpleNamespace):
    __HASH__ = "#"
    _logger_ = logging.getLogger(__name__)
    # ``_`` is bound to a data descriptor after the class is defined,
    # see ``recursivenamespace._ = _Descriptor()`` below.

    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
        **kwargs: Any,
    ) -> None:
        if data is None:
            data = {}
        if accepted_iter_types is None:
            accepted_iter_types = []

        self._key_ = ""
        self._use__raw_key_ = use_raw_key
        self._supported__types_ = list(
            dict.fromkeys([list, tuple, set] + accepted_iter_types)
        )

        self._protected__keys_: set[str] = set()  # init attr in __dict__
        self._protected__keys_ = set(self.__dict__.keys()) | _PUBLIC_CLASS_ATTRS

        if isinstance(data, dict):
            kwargs.update(data)

        for key, val in kwargs.items():
            key = self._re_(key)
            if isinstance(val, dict):
                val = recursivenamespace(val, accepted_iter_types, use_raw_key)
                _StaticImpl.set_key(val, key)
            elif isinstance(val, recursivenamespace):
                _StaticImpl.set_key(val, key)
            else:
                val = self._process_(val)
            self[key] = val

    def _process_(
        self,
        val: Any,
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> Any:
        if isinstance(val, dict):
            return recursivenamespace(val, accepted_iter_types, use_raw_key)
        elif isinstance(val, str):
            return val
        elif hasattr(val, "__iter__") and type(val) in self._supported__types_:
            lst = [
                self._process_(v, accepted_iter_types, use_raw_key) for v in val
            ]
            try:
                return type(val)(lst)
            except Exception as e:
                print(
                    f"Failed to make iterable object of type {type(val)}",
                    e,
                    file=sys.stderr,
                )
                return val
        else:
            return val

    def _re_(self, key: str) -> str:
        return key if self._use__raw_key_ else _KEY_NORMALIZE_RE.sub("_", key)

    def _remove_protected_key_(self, key: str) -> None:  # NOSONAR
        """Use with be-careful!"""
        self._protected__keys_.remove(key)
        self.__dict__.pop(key)

    # ── Dunders ───────────────────────────────────────────────────

    def __eq__(self, other: object) -> bool:
        if isinstance(other, recursivenamespace):
            return vars(self) == vars(other)
        elif isinstance(other, dict):
            return vars(self) == other
        return False

    def __repr__(self) -> str:
        s = ""
        for k, v in _StaticImpl.items(self):
            s += f"{k}={v}, "
        if len(s) > 0:
            s = s[:-2]
        return f"RNS({s})"

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self) -> int:
        return sum(1 for k in self.__dict__ if k not in self._protected__keys_)

    def __delattr__(self, key: str) -> None:
        key = self._re_(key)
        if key in self._protected__keys_:
            raise AttributeError(
                f"The key '{key}' is protected — reserved method proxy"
                if key == "_"
                else f"The key '{key}' is protected."
            )
        del self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        key = self._re_(key)
        if key in self._protected__keys_:
            raise KeyError(f"The key '{key}' is protected.")
        setattr(self, key, value)

    def __getitem__(self, key: str) -> Any:
        key = self._re_(key)
        if key in self._protected__keys_:
            raise KeyError(f"The key '{key}' is protected.")
        return getattr(self, key)

    def __delitem__(self, key: str) -> None:
        key = self._re_(key)
        delattr(self, key)

    def __contains__(self, key: str) -> bool:
        key = self._re_(key)
        return key in self.__dict__

    def __copy__(self) -> "recursivenamespace":
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo: Dict[int, Any]) -> "recursivenamespace":
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __iter__(self) -> Iterator[str]:
        if sys._getframe(1).f_code.co_name == "dict":
            return iter(_StaticImpl.to_dict(self))
        return iter(_StaticImpl.keys(self))

    # ── Private chain-key helpers ────────────────────────────────

    def _iter_to_dict_(self, iterable: Any) -> Any:
        elements = []
        for val in iterable:
            if isinstance(val, recursivenamespace):
                elements.append(_StaticImpl.to_dict(val))
            elif isinstance(val, dict):
                elements.append(val)
            elif (
                hasattr(val, "__iter__")
                and type(val) in self._supported__types_
            ):
                elements.append(self._iter_to_dict_(val))
            else:
                elements.append(val)
        return type(iterable)(elements)

    def _chain_set_array_(self, key: str, subs: List[str], value: Any) -> None:
        target = self._get_or_create_list_target_(key)
        if not subs:
            raise KeyError(
                f"Invalid array key '{key}'. Required the 'index' as well, "
                f"e.g.: key[].#"
            )
        head, *rest = subs
        if head == self.__HASH__:
            self._array_append_(target, rest, value)
        else:
            self._array_set_at_(target, key, int(head), rest, value)

    def _get_or_create_list_target_(self, key: str) -> List[Any]:
        if not hasattr(self, key):
            self[key] = []
        target = self[key]
        if not isinstance(target, list):
            raise KeyError(
                f"Invalid array key '{key}'. It is required a list, but "
                f"got {type(target)}"
            )
        return target

    def _array_append_(
        self, target: List[Any], sub_keys: List[str], value: Any
    ) -> None:
        if not sub_keys:
            target.append(value)
            return
        new_item = recursivenamespace(
            None, self._supported__types_, self._use__raw_key_
        )
        _StaticImpl.val_set(new_item, utils.join_key(sub_keys), value)
        target.append(new_item)

    def _array_set_at_(
        self,
        target: List[Any],
        key: str,
        index: int,
        sub_keys: List[str],
        value: Any,
    ) -> None:
        if not sub_keys:
            target[index] = value
            return
        child = target[index]
        sub_key = utils.join_key(sub_keys)
        if isinstance(child, recursivenamespace):
            _StaticImpl.val_set(child, sub_key, value)
        else:
            raise SetChainKeyError(child, f"{key}[{index}]", sub_key)

    def _chain_set_value_(self, key: str, subs: List[str], value: Any) -> None:
        if not hasattr(self, key):
            self[key] = recursivenamespace(
                None, self._supported__types_, self._use__raw_key_
            )
        target = self[key]
        sub_key = utils.join_key(subs)
        if isinstance(target, recursivenamespace):
            _StaticImpl.val_set(target, sub_key, value)
        else:
            raise SetChainKeyError(target, key, sub_key)

    def _chain_get_array_(self, key: str, subs: List[str]) -> Any:
        target = self[key]
        subs_len = len(subs)
        if not isinstance(target, list):
            raise KeyError(
                f"Invalid array key '{key}'. It is required a list, but got {type(target)}"
            )
        if subs_len == 0:
            raise KeyError(
                f"Invalid array key '{key}'. Required the 'index' as well, e.g.: key[].#"
            )
        index = -1 if subs[0] == self.__HASH__ else int(subs[0])
        subs = subs[1:]
        subs_len -= 1

        if subs_len == 0:
            return target[index]

        target = target[index]
        sub_key = utils.join_key(subs)
        if isinstance(target, recursivenamespace):
            return _StaticImpl.val_get(target, sub_key)
        elif subs_len == 1:
            return getattr(target, sub_key)
        else:
            raise GetChainKeyError(target, key, sub_key)

    def _chain_get_value_(self, key: str, subs: List[str]) -> Any:
        target = self[key]
        sub_key = utils.join_key(subs)
        if isinstance(target, recursivenamespace):
            return _StaticImpl.val_get(target, sub_key)
        elif len(subs) == 1:
            return getattr(target, sub_key)
        else:
            raise GetChainKeyError(target, key, sub_key)

    @staticmethod
    def _toml_escape_str_(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    @staticmethod
    def _toml_format_scalar_(value: Any) -> str:
        """Render a primitive TOML value (caller already handled None)."""
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, str):
            return f'"{recursivenamespace._toml_escape_str_(value)}"'
        return str(value)

    @staticmethod
    def _toml_format_array_(key: str, value: Any) -> str:
        """Render ``key = [v1, v2, ...]`` or a comment if not serializable."""
        if not all(isinstance(v, (str, int, float, bool)) for v in value):
            return f"# {key} = [complex array - not serialized]"
        parts = [recursivenamespace._toml_format_scalar_(v) for v in value]
        return f"{key} = [{', '.join(parts)}]"

    @staticmethod
    def _toml_format_line_(key: str, value: Any) -> Optional[str]:
        """Render a single ``key = value`` line, or None to skip the entry."""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return f"{key} = {recursivenamespace._toml_format_scalar_(value)}"
        if isinstance(value, (list, tuple)):
            return recursivenamespace._toml_format_array_(key, value)
        return f"# {key} = [type {type(value).__name__} not supported]"

    @staticmethod
    def _dict_to_toml_(data: Dict[str, Any], prefix: str = "") -> str:
        """Convert dict to TOML format."""
        lines: List[str] = []
        tables: List[tuple[str, Dict[str, Any]]] = []

        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                tables.append((full_key, value))
                continue
            line = recursivenamespace._toml_format_line_(key, value)
            if line is not None:
                lines.append(line)

        for table_key, table_value in tables:
            lines.append("")
            lines.append(f"[{table_key}]")
            lines.append(recursivenamespace._dict_to_toml_(table_value, ""))

        return "\n".join(lines)

    # ── Classmethod factories (kept on the class, no deprecation) ─

    @classmethod
    def from_json(
        cls,
        json_str: str,
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> "recursivenamespace":
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise SerializationError(
                    f"JSON must represent a dict, got {type(data)}"
                )
            return cls(data, accepted_iter_types, use_raw_key)
        except json.JSONDecodeError as e:
            raise SerializationError(f"Invalid JSON: {e}")
        except Exception as e:
            raise SerializationError(f"Failed to parse JSON: {e}")

    @classmethod
    def load_json(
        cls,
        filepath: Union[str, Path],
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> "recursivenamespace":
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return cls.from_json(f.read(), accepted_iter_types, use_raw_key)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise SerializationError(f"Failed to load JSON file: {e}")

    @classmethod
    def from_toml(
        cls,
        toml_str: str,
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> "recursivenamespace":
        if tomllib is None:
            raise ImportError(
                "TOML support requires Python 3.11+ or 'tomli' package. "
                "Install with: pip install tomli"
            )
        try:
            data = tomllib.loads(toml_str)
            return cls(data, accepted_iter_types, use_raw_key)
        except Exception as e:
            raise SerializationError(f"Failed to parse TOML: {e}")

    @classmethod
    def load_toml(
        cls,
        filepath: Union[str, Path],
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> "recursivenamespace":
        if tomllib is None:
            raise ImportError(
                "TOML support requires Python 3.11+ or 'tomli' package. "
                "Install with: pip install tomli"
            )
        try:
            with open(filepath, "rb") as f:
                data = tomllib.load(f)
                return cls(data, accepted_iter_types, use_raw_key)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise SerializationError(f"Failed to load TOML file: {e}")

    # ── Public-method shims (warn + delegate to _StaticImpl) ──────

    @_deprecated
    def set_key(self, key: str) -> None:
        return _StaticImpl.set_key(self, key)

    @_deprecated
    def get_key(self) -> str:
        return _StaticImpl.get_key(self)

    @_deprecated
    def update(self, data: Union[Dict[str, Any], "recursivenamespace"]) -> None:
        return _StaticImpl.update(self, data)

    @_deprecated
    def copy(self) -> "recursivenamespace":
        return _StaticImpl.copy(self)

    @_deprecated
    def deepcopy(self) -> "recursivenamespace":
        return _StaticImpl.deepcopy(self)

    @_deprecated
    def pop(self, key: str, default: Optional[T] = None) -> Union[Any, T]:
        return _StaticImpl.pop(self, key, default)

    @_deprecated
    def items(self) -> List[tuple[str, Any]]:
        return _StaticImpl.items(self)

    @_deprecated
    def keys(self) -> List[str]:
        return _StaticImpl.keys(self)

    @_deprecated
    def values(self) -> List[Any]:
        return _StaticImpl.values(self)

    @_deprecated
    def to_dict(self, flatten_sep: Union[str, bool] = False) -> Dict[str, Any]:
        return _StaticImpl.to_dict(self, flatten_sep)

    @_deprecated
    def val_set(self, key: str, value: Any) -> None:
        return _StaticImpl.val_set(self, key, value)

    @_deprecated
    def val_get(self, key: str) -> Any:
        return _StaticImpl.val_get(self, key)

    @_deprecated
    def get_or_else(
        self, key: str, or_else: Optional[T] = None, show_log: bool = False
    ) -> Union[Any, T]:
        return _StaticImpl.get_or_else(self, key, or_else, show_log)

    @_deprecated
    def as_schema(self, schema_cls: type[T], /, **kwargs: Any) -> T:
        return _StaticImpl.as_schema(self, schema_cls, **kwargs)

    @_deprecated
    def temporary(
        self,
    ) -> contextlib.AbstractContextManager["recursivenamespace"]:
        return _StaticImpl.temporary(self)

    @_deprecated
    def overlay(
        self, overrides: Dict[str, Any]
    ) -> contextlib.AbstractContextManager["recursivenamespace"]:
        return _StaticImpl.overlay(self, overrides)

    @_deprecated
    def to_json(
        self,
        indent: Optional[int] = 2,
        sort_keys: bool = False,
        ensure_ascii: bool = True,
        **kwargs: Any,
    ) -> str:
        return _StaticImpl.to_json(
            self, indent, sort_keys, ensure_ascii, **kwargs
        )

    @_deprecated
    def save_json(
        self,
        filepath: Union[str, Path],
        indent: Optional[int] = 2,
        **kwargs: Any,
    ) -> None:
        return _StaticImpl.save_json(self, filepath, indent, **kwargs)

    @_deprecated
    def to_toml(self) -> str:
        return _StaticImpl.to_toml(self)

    @_deprecated
    def save_toml(self, filepath: Union[str, Path]) -> None:
        return _StaticImpl.save_toml(self, filepath)


# ──────────────────────────────────────────────────────────────────
# _StaticImpl: single source of truth for the 20 public methods.
# Every method takes the RNS instance explicitly as the first argument.
# Internal cross-method recursion uses _StaticImpl.<other>(rns_ins, ...)
# directly — never the shim — so no deprecation warnings fire on hops
# the user did not make.
# ──────────────────────────────────────────────────────────────────


class _StaticImpl:
    """Real implementation of RNS public instance methods.

    All callers (the class shims, the ``_BoundProxy`` for ``obj._``,
    direct ``RNS._.method(obj, ...)`` calls, and internal recursion)
    converge on these staticmethods.
    """

    @staticmethod
    def set_key(rns_ins: "recursivenamespace", key: str) -> None:
        rns_ins._key_ = rns_ins._re_(key)

    @staticmethod
    def get_key(rns_ins: "recursivenamespace") -> str:
        return rns_ins._key_

    @staticmethod
    def update(
        rns_ins: "recursivenamespace",
        data: Union[Dict[str, Any], "recursivenamespace"],
    ) -> None:
        try:
            if not isinstance(data, recursivenamespace):
                data = recursivenamespace(
                    data,
                    rns_ins._supported__types_,
                    rns_ins._use__raw_key_,
                )
        except Exception as e:
            raise TypeError(
                f"Failed to update with data of type {type(data)}"
            ) from e
        for key, val in _StaticImpl.items(data):
            rns_ins[key] = val

    @staticmethod
    def copy(rns_ins: "recursivenamespace") -> "recursivenamespace":
        return rns_ins.__copy__()

    @staticmethod
    def deepcopy(rns_ins: "recursivenamespace") -> "recursivenamespace":
        memo: Dict[int, Any] = {}
        return rns_ins.__deepcopy__(memo)

    @staticmethod
    def pop(
        rns_ins: "recursivenamespace",
        key: str,
        default: Optional[T] = None,
    ) -> Union[Any, T]:
        key = rns_ins._re_(key)
        if key in rns_ins._protected__keys_:
            raise KeyError(f"The key '{key}' is protected.")
        if key in rns_ins.__dict__:
            val = rns_ins.__dict__[key]
            del rns_ins.__dict__[key]
            return val
        return default

    @staticmethod
    def items(rns_ins: "recursivenamespace") -> List[tuple[str, Any]]:
        return [
            (k, v)
            for k, v in rns_ins.__dict__.items()
            if k not in rns_ins._protected__keys_
        ]

    @staticmethod
    def keys(rns_ins: "recursivenamespace") -> List[str]:
        return [
            k
            for k in rns_ins.__dict__.keys()
            if k not in rns_ins._protected__keys_
        ]

    @staticmethod
    def values(rns_ins: "recursivenamespace") -> List[Any]:
        return [
            v
            for k, v in rns_ins.__dict__.items()
            if k not in rns_ins._protected__keys_
        ]

    @staticmethod
    def to_dict(
        rns_ins: "recursivenamespace",
        flatten_sep: Union[str, bool] = False,
    ) -> Dict[str, Any]:
        """Convert RNS to dict. If flatten_sep is set, flatten keys."""
        pairs = []
        for k, v in _StaticImpl.items(rns_ins):
            if isinstance(v, recursivenamespace):
                pairs.append((k, _StaticImpl.to_dict(v)))
            elif isinstance(v, dict):
                pairs.append((k, v))
            elif (
                hasattr(v, "__iter__") and type(v) in rns_ins._supported__types_
            ):
                pairs.append((k, rns_ins._iter_to_dict_(v)))
            else:
                pairs.append((k, v))
        d = dict(pairs)
        if flatten_sep:
            sep = flatten_sep if isinstance(flatten_sep, str) else "."
            d = dict(utils.flatten_as_dict(d, sep=sep))
        return d

    @staticmethod
    def val_set(rns_ins: "recursivenamespace", key: str, value: Any) -> None:
        """Set the value by key. Supports chain-keys and arrays.

        Patterns: ``a.b.c``, ``a.b.c[].<i>``, ``a.b.c[].#``, etc.
        """
        key, *subs = utils.split_key(key)
        key = utils.unescape_key(key)
        subs_len = len(subs)
        is_array = key[-2:] == utils.KEY_ARRAY

        if subs_len == 0 and not is_array:
            rns_ins[key] = value
            return

        if is_array:
            rns_ins._chain_set_array_(key[:-2], subs, value)
        else:
            rns_ins._chain_set_value_(key, subs, value)

    @staticmethod
    def val_get(rns_ins: "recursivenamespace", key: str) -> Any:
        """Get the value by key. Supports chain-keys and arrays."""
        key, *subs = utils.split_key(key)
        key = utils.unescape_key(key)
        subs_len = len(subs)
        is_array = key[-2:] == utils.KEY_ARRAY

        if subs_len == 0 and not is_array:
            return rns_ins[key]

        if is_array:
            return rns_ins._chain_get_array_(key[:-2], subs)
        return rns_ins._chain_get_value_(key, subs)

    @staticmethod
    def get_or_else(
        rns_ins: "recursivenamespace",
        key: str,
        or_else: Optional[T] = None,
        show_log: bool = False,
    ) -> Union[Any, T]:
        try:
            return _StaticImpl.val_get(rns_ins, key)
        except Exception:
            if show_log:
                rns_ins._logger_.warning(f"KeyNotFound - {key}", exc_info=True)
            return or_else

    @staticmethod
    def as_schema(
        rns_ins: "recursivenamespace",
        schema_cls: type[T],
        /,
        **kwargs: Any,
    ) -> T:
        if not dataclasses.is_dataclass(schema_cls):
            raise TypeError("The 'schema_cls' must be a DataClass type.")
        fields = dataclasses.fields(schema_cls)
        for field in fields:
            name = field.name
            kwargs[name] = rns_ins[name]
        return schema_cls(**kwargs)

    @staticmethod
    @contextlib.contextmanager
    def temporary(
        rns_ins: "recursivenamespace",
    ) -> Generator["recursivenamespace", None, None]:
        """Yield a deep copy; the original is untouched."""
        yield _StaticImpl.deepcopy(rns_ins)

    @staticmethod
    @contextlib.contextmanager
    def overlay(
        rns_ins: "recursivenamespace", overrides: Dict[str, Any]
    ) -> Generator["recursivenamespace", None, None]:
        """Temporarily apply *overrides*, restore on exit."""
        originals: Dict[str, Any] = {}
        added_keys: List[str] = []

        for key, value in overrides.items():
            nk = rns_ins._re_(key)
            if nk in rns_ins.__dict__ and nk not in rns_ins._protected__keys_:
                originals[nk] = rns_ins.__dict__[nk]
            else:
                added_keys.append(nk)
            rns_ins[key] = value

        try:
            yield rns_ins
        finally:
            for k, v in originals.items():
                rns_ins.__dict__[k] = v
            for k in added_keys:
                rns_ins.__dict__.pop(k, None)

    @staticmethod
    def to_json(
        rns_ins: "recursivenamespace",
        indent: Optional[int] = 2,
        sort_keys: bool = False,
        ensure_ascii: bool = True,
        **kwargs: Any,
    ) -> str:
        try:
            return json.dumps(
                _StaticImpl.to_dict(rns_ins),
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii,
                **kwargs,
            )
        except (TypeError, ValueError) as e:
            raise SerializationError(f"Failed to serialize to JSON: {e}")

    @staticmethod
    def save_json(
        rns_ins: "recursivenamespace",
        filepath: Union[str, Path],
        indent: Optional[int] = 2,
        **kwargs: Any,
    ) -> None:
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(_StaticImpl.to_json(rns_ins, indent=indent, **kwargs))
        except Exception as e:
            raise SerializationError(f"Failed to save JSON file: {e}")

    @staticmethod
    def to_toml(rns_ins: "recursivenamespace") -> str:
        try:
            return recursivenamespace._dict_to_toml_(
                _StaticImpl.to_dict(rns_ins)
            )
        except Exception as e:
            raise SerializationError(f"Failed to serialize to TOML: {e}")

    @staticmethod
    def save_toml(
        rns_ins: "recursivenamespace", filepath: Union[str, Path]
    ) -> None:
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(_StaticImpl.to_toml(rns_ins))
        except Exception as e:
            raise SerializationError(f"Failed to save TOML file: {e}")


# ──────────────────────────────────────────────────────────────────
# Bound proxy + descriptor for ``obj._``
# ──────────────────────────────────────────────────────────────────


class _BoundProxy:
    """Curries the owner into ``_StaticImpl`` calls so ``obj._.to_dict()``
    works as a normal bound-method call."""

    __slots__ = ("_owner",)

    def __init__(self, owner: "recursivenamespace") -> None:
        object.__setattr__(self, "_owner", owner)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        attr = getattr(_StaticImpl, name, None)
        if attr is None or not callable(attr):
            raise AttributeError(name)
        return functools.partial(attr, self._owner)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("RNS '_' proxy is read-only")

    def __dir__(self) -> List[str]:
        return [n for n in dir(_StaticImpl) if not n.startswith("_")]

    def __repr__(self) -> str:
        return f"<RNS method proxy for 0x{id(self._owner):x}>"


class _Descriptor:
    """Data descriptor exposing ``recursivenamespace._``.

    Class access (``RNS._``) returns the static container so callers
    can write ``RNS._.to_dict(obj)``. Instance access (``obj._``)
    returns a fresh ``_BoundProxy`` so callers can write
    ``obj._.to_dict()`` bound-method style. The descriptor's
    ``__set__`` / ``__delete__`` make it a *data* descriptor that
    can't be shadowed by instance ``__dict__`` assignments.
    """

    def __get__(
        self,
        instance: Optional["recursivenamespace"],
        owner: type,
    ) -> Any:
        if instance is None:
            return _StaticImpl
        return _BoundProxy(instance)

    def __set__(self, instance: "recursivenamespace", value: Any) -> None:
        raise AttributeError("Cannot assign to '_' — reserved method proxy")

    def __delete__(self, instance: "recursivenamespace") -> None:
        raise AttributeError("Cannot delete '_' — reserved method proxy")


# Bind the descriptor and compute the protected-attribute set.
# Use setattr so static type checkers don't flag the dynamic attribute.
setattr(recursivenamespace, "_", _Descriptor())

# Names of class-level attributes that user data must not shadow.
# Filter: everything not starting with ``__`` — this keeps public
# methods, the ``_`` proxy, ``_logger_``, and private helpers like
# ``_re_`` / ``_process_`` / ``_chain_*_`` in the protected set.
_PUBLIC_CLASS_ATTRS: frozenset[str] = frozenset(
    name for name in dir(recursivenamespace) if not name.startswith("__")
)


# %%
def _rns_normalize_return_(
    ret_val: Any, use_chain_key: bool, props: str
) -> Any:
    """Convert a decorated function's return value into ``data`` for RNS.

    Recognised shapes: a list of ``KV_Pair`` (chain-key mode), a dict,
    a dataclass instance, or any other scalar (wrapped under ``props``).
    """
    if (
        use_chain_key
        and isinstance(ret_val, list)
        and (not ret_val or isinstance(ret_val[0], utils.KV_Pair))
    ):
        return ret_val
    if isinstance(ret_val, dict):
        return ret_val
    if dataclasses.is_dataclass(ret_val):
        return dataclasses.asdict(ret_val)  # type: ignore[arg-type]
    return {props: ret_val}


def _rns_build_from_data_(
    data: Any,
    accepted_iter_types_list: List[type],
    use_raw_key: bool,
    use_chain_key: bool,
) -> "recursivenamespace":
    if not use_chain_key:
        return recursivenamespace(data, accepted_iter_types_list, use_raw_key)
    ret = recursivenamespace(None, accepted_iter_types_list, use_raw_key)
    items = data.items() if isinstance(data, dict) else data
    for key, value in items:
        _StaticImpl.val_set(ret, key, value)
    return ret


def rns(
    accepted_iter_types: Optional[List[type]] = None,
    use_raw_key: bool = False,
    use_chain_key: bool = False,
    props: str = "props",
) -> Callable[[Callable[..., Any]], Callable[..., recursivenamespace]]:
    """Create RNS object"""
    accepted_iter_types_list: List[type] = (
        [] if accepted_iter_types is None else accepted_iter_types
    )

    def fn_wrapper(
        func: Callable[..., Any],
    ) -> Callable[..., recursivenamespace]:  # NOSONAR
        @functools.wraps(func)
        def create_rns(*args: Any, **kwargs: Any) -> recursivenamespace:
            ret_val = func(*args, **kwargs)
            data = _rns_normalize_return_(ret_val, use_chain_key, props)
            return _rns_build_from_data_(
                data, accepted_iter_types_list, use_raw_key, use_chain_key
            )

        return create_rns

    return fn_wrapper
