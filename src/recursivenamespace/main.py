#############################
# Fork: https://github.com/HessamLa/recursivenamespace
# %%
from __future__ import annotations

import contextlib
import dataclasses
import json
import logging
import re
import sys
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
from copy import deepcopy
from types import SimpleNamespace
from pathlib import Path
import functools

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


class recursivenamespace(SimpleNamespace):
    __HASH__ = "#"
    __logger = logging.getLogger(__name__)

    # TODO(refactor): reduce cognitive complexity (~16) — nested type checks in loop
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

        self.__key_ = ""
        self.__use_raw_key_ = use_raw_key
        self.__supported_types_ = list(
            dict.fromkeys([list, tuple, set] + accepted_iter_types)
        )

        self.__protected_keys_: set[str] = set()  # init attr in __dict__
        self.__protected_keys_ = set(self.__dict__.keys())

        if isinstance(data, dict):
            kwargs.update(data)

        for key, val in kwargs.items():
            key = self.__re(key)
            if isinstance(val, dict):
                val = recursivenamespace(val, accepted_iter_types, use_raw_key)
                val.set_key(key)
            elif isinstance(val, recursivenamespace):
                val.set_key(key)
            else:
                val = self.__process(val)
            # setattr(self, key, val)
            self[key] = val

    # TODO(refactor): reduce cognitive complexity (~17) — isinstance branches + try/except
    def __process(
        self,
        val: Any,
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> Any:
        if isinstance(val, dict):
            return recursivenamespace(val, accepted_iter_types, use_raw_key)
        elif isinstance(val, str):
            return val
        elif hasattr(val, "__iter__") and type(val) in self.__supported_types_:
            lst = [
                self.__process(v, accepted_iter_types, use_raw_key) for v in val
            ]
            try:
                return type(val)(
                    lst
                )  # the type is assumed to support list-to-type conversion
            except Exception as e:
                print(
                    f"Failed to make iterable object of type {type(val)}",
                    e,
                    file=sys.stderr,
                )
                return val
        else:
            return val

    def __re(self, key: str) -> str:
        return key if self.__use_raw_key_ else _KEY_NORMALIZE_RE.sub("_", key)

    def set_key(self, key: str) -> None:
        self.__key_ = self.__re(key)

    def get_key(self) -> str:
        return self.__key_

    def update(self, data: Union[Dict[str, Any], "recursivenamespace"]) -> None:
        try:
            if not isinstance(data, recursivenamespace):
                data = recursivenamespace(
                    data, self.__supported_types_, self.__use_raw_key_
                )
        except Exception as e:
            raise TypeError(
                f"Failed to update with data of type {type(data)}"
            ) from e
        for key, val in data.items():
            self[key] = val

    def __remove_protected_key(self, key: str) -> None:  # NOSONAR
        """Use with be-careful!"""
        self.__protected_keys_.remove(key)
        self.__dict__.pop(key)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, recursivenamespace):
            return vars(self) == vars(other)
        elif isinstance(other, dict):
            return vars(self) == other
        return False

    def __repr__(self) -> str:
        s = ""
        for k, v in self.items():
            s += f"{k}={v}, "
        if len(s) > 0:
            s = s[:-2]  # remove the last ','
        s = f"RNS({s})"
        return s

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self) -> int:
        return len(self.__dict__) - len(self.__protected_keys_)

    def __delattr__(self, key: str) -> None:
        key = self.__re(key)
        if key not in self.__protected_keys_:
            # delattr(self, key)
            del self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        key = self.__re(key)
        if key in self.__protected_keys_:
            raise KeyError(f"The key '{key}' is protected.")
        setattr(self, key, value)

    def __getitem__(self, key: str) -> Any:
        key = self.__re(key)
        if key in self.__protected_keys_:
            raise KeyError(f"The key '{key}' is protected.")
        return getattr(self, key)

    def __delitem__(self, key: str) -> None:
        key = self.__re(key)
        delattr(self, key)

    def __contains__(self, key: str) -> bool:
        key = self.__re(key)
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

    def copy(self) -> "recursivenamespace":
        return self.__copy__()

    def deepcopy(self) -> "recursivenamespace":
        memo: Dict[int, Any] = {}
        return self.__deepcopy__(memo)

    def pop(self, key: str, default: Optional[T] = None) -> Union[Any, T]:
        key = self.__re(key)
        if key in self.__protected_keys_:
            raise KeyError(f"The key '{key}' is protected.")
        if key in self.__dict__:
            val = self.__dict__[key]
            del self.__dict__[key]
            return val
        else:
            return default

    def items(self) -> List[tuple[str, Any]]:
        return [
            (k, v)
            for k, v in self.__dict__.items()
            if k not in self.__protected_keys_
        ]

    def keys(self) -> List[str]:
        return [
            k for k in self.__dict__.keys() if k not in self.__protected_keys_
        ]

    def values(self) -> List[Any]:
        return [
            v
            for k, v in self.__dict__.items()
            if k not in self.__protected_keys_
        ]

    def __iter__(self) -> Iterator[str]:
        if sys._getframe(1).f_code.co_name == "dict":
            return iter(self.to_dict())
        return iter(self.keys())

    # TODO(refactor): reduce cognitive complexity (~15) — nested isinstance branches
    def to_dict(self, flatten_sep: Union[str, bool] = False) -> Dict[str, Any]:
        """Convert the recursivenamespace object to a dictionary.
        If flatten_sep is not False, then the keys are flattened using the separator.
        """
        pairs = []
        for k, v in self.items():
            if isinstance(v, recursivenamespace):
                pairs.append((k, v.to_dict()))
            elif isinstance(v, dict):
                pairs.append((k, v))
            elif hasattr(v, "__iter__") and type(v) in self.__supported_types_:
                pairs.append((k, self.__iter_to_dict(v)))
            else:
                pairs.append((k, v))
        d = dict(pairs)
        if flatten_sep:
            sep = flatten_sep if isinstance(flatten_sep, str) else "."
            d = dict(utils.flatten_as_dict(d, sep=sep))
        return d

    def __iter_to_dict(self, iterable: Any) -> Any:
        elements = []
        for val in iterable:
            if isinstance(val, recursivenamespace):
                elements.append(val.to_dict())
            elif isinstance(val, dict):
                elements.append(val)
            elif (
                hasattr(val, "__iter__")
                and type(val) in self.__supported_types_
            ):
                elements.append(self.__iter_to_dict(val))
            else:
                elements.append(val)
        return type(iterable)(elements)

    # TODO(refactor): reduce cognitive complexity (~18) — 4-level nesting with index branching
    def __chain_set_array(self, key: str, subs: List[str], value: Any) -> None:
        # if the `key` not existed, then create it ??
        if not hasattr(self, key):
            self[key] = []
        target = self[key]
        subs_len = len(subs)
        # validate:
        if not isinstance(target, list):
            raise KeyError(
                f"Invalid array key '{key}'. It is required a list, but got {type(target)}"
            )
        if subs_len == 0:
            raise KeyError(
                f"Invalid array key '{key}'. Required the 'index' as well, e.g.: key[].#"
            )
        # get the `index`:
        index = None if subs[0] == self.__HASH__ else int(subs[0])
        # remove the `index` from sub-key:
        subs = subs[1:]
        subs_len -= 1

        if index is None:  # if APPEND the value ??
            if subs_len == 0:
                # 1) if append the value to the target array
                target.append(value)
            else:
                # 2) if chain-append the value to the target array,
                # then create a "new-item" and set the value for sub-key:
                new_item = recursivenamespace(
                    None, self.__supported_types_, self.__use_raw_key_
                )
                sub_key = utils.join_key(subs)
                new_item.val_set(sub_key, value)
                target.append(new_item)
        else:  # if SET the value ??
            if subs_len == 0:
                # 1) if set the value to the target array at "index"
                target[index] = value
            else:
                # 2) if chain-set the value to the target array at "index",
                # then get the value at "index" and set the value for sub-key:
                target = target[index]
                sub_key = utils.join_key(subs)
                if isinstance(target, recursivenamespace):
                    target.val_set(sub_key, value)
                else:
                    raise SetChainKeyError(target, f"{key}[{index}]", sub_key)

    def __chain_set_value(self, key: str, subs: List[str], value: Any) -> None:
        # if the `key` not existed, then create it ??
        if not hasattr(self, key):
            self[key] = recursivenamespace(
                None, self.__supported_types_, self.__use_raw_key_
            )
        target = self[key]
        sub_key = utils.join_key(subs)
        if isinstance(target, recursivenamespace):
            target.val_set(sub_key, value)
        else:
            raise SetChainKeyError(target, key, sub_key)

    def val_set(self, key: str, value: Any) -> None:
        """Set the value by key.

        Supported "chain-key" patterns:

        - ``a.b.c`` -- set value to the item "c"
        - ``a.b.c[].<i>`` -- set value at index i of array "c"
        - ``a.b.c[].#`` -- append value to end of array "c"
        - ``a.b.c[].<i>.x[].<j>`` -- set value at index j of nested array "x"
        - ``a.b.c[].<i>.x[].#`` -- append to nested array "x"
        - ``a.b.c[].#.x[].#`` -- append new item with nested array append

        Args:
            key: The key to set.
            value: The value to set.

        Raises:
            KeyError: When trying to set a protected value.
            SetChainKeyError: When chain-key target is not an RNS type.
        """
        # @ raw_key = key
        key, *subs = utils.split_key(key)
        key = utils.unescape_key(key)
        subs_len = len(subs)
        is_array = key[-2:] == utils.KEY_ARRAY

        # if not chain-key/array SET ??
        if subs_len == 0 and not is_array:
            self[key] = value
            return

        # SET to an array
        if is_array:
            self.__chain_set_array(key[:-2], subs, value)
        else:  # SET the value
            self.__chain_set_value(key, subs, value)

    # TODO(refactor): reduce cognitive complexity (~16) — validation + index branching
    def __chain_get_array(self, key: str, subs: List[str]) -> Any:
        target = self[key]
        subs_len = len(subs)
        # validate:
        if not isinstance(target, list):
            raise KeyError(
                f"Invalid array key '{key}'. It is required a list, but got {type(target)}"
            )
        if subs_len == 0:
            raise KeyError(
                f"Invalid array key '{key}'. Required the 'index' as well, e.g.: key[].#"
            )
        # get the `index`:
        index = -1 if subs[0] == self.__HASH__ else int(subs[0])
        # remove the `index` from sub-key:
        subs = subs[1:]
        subs_len -= 1

        # if GET the value by `index`
        if subs_len == 0:
            return target[index]

        # @else: GET value of sub-key
        target = target[index]
        sub_key = utils.join_key(subs)
        if isinstance(target, recursivenamespace):
            return target.val_get(sub_key)
        elif subs_len == 1:
            return getattr(target, sub_key)
        else:
            raise GetChainKeyError(target, key, sub_key)

    def __chain_get_value(self, key: str, subs: List[str]) -> Any:
        target = self[key]
        sub_key = utils.join_key(subs)
        if isinstance(target, recursivenamespace):
            return target.val_get(sub_key)
        elif len(subs) == 1:
            return getattr(target, sub_key)
        else:
            raise GetChainKeyError(target, key, sub_key)

    def val_get(self, key: str) -> Any:
        """Get the value by key.

        Supported "chain-key" patterns:

        - ``a.b.c`` -- get the item "c"
        - ``a.b.c[].<i>`` -- get item at index i of array "c"
        - ``a.b.c[].#`` -- get the last item of array "c" (same as -1)
        - ``a.b.c[].<i>.x[].<j>`` -- get item at index j of nested array "x"

        Args:
            key: The key to get.

        Returns:
            The value if the key exists.

        Raises:
            KeyError: When trying to get a protected value or key doesn't exist.
            GetChainKeyError: When chain-key target is not an RNS type.
        """
        # @ raw_key = key
        key, *subs = utils.split_key(key)
        key = utils.unescape_key(key)
        subs_len = len(subs)
        is_array = key[-2:] == utils.KEY_ARRAY

        # if not chain-key/array GET ??
        if subs_len == 0 and not is_array:
            return self[key]

        # GET from an array
        if is_array:
            return self.__chain_get_array(key[:-2], subs)
        # @else: GET the value
        return self.__chain_get_value(key, subs)

    def get_or_else(
        self, key: str, or_else: Optional[T] = None, show_log: bool = False
    ) -> Union[Any, T]:
        """Get the value by key.
        Supported "chain-key", e.g.: a.b.c

        Args:
            key (str): The key to get

        Returns:
            any: The value if the `key` is existed, else return `None`.
        """
        try:
            return self.val_get(key)
        except Exception:
            # skip the error.
            if show_log:
                self.__logger.warning(f"KeyNotFound - {key}", exc_info=True)
            return or_else

    def as_schema(self, schema_cls: type[T], /, **kwargs: Any) -> T:
        if not dataclasses.is_dataclass(schema_cls):
            raise TypeError("The 'schema_cls' must be a DataClass type.")
        # @else:
        fields = dataclasses.fields(schema_cls)
        for field in fields:
            name = field.name
            kwargs[name] = self[name]
        return schema_cls(**kwargs)

    # Context Managers

    @contextlib.contextmanager
    def temporary(
        self,
    ) -> Generator["recursivenamespace", None, None]:
        """Yield a deep copy; the original is untouched.

        Example::

            with config.temporary() as tmp:
                tmp.debug = True   # modify freely
            assert config.debug is False  # original unchanged
        """
        yield self.deepcopy()

    @contextlib.contextmanager
    def overlay(
        self, overrides: Dict[str, Any]
    ) -> Generator["recursivenamespace", None, None]:
        """Temporarily apply *overrides*, restore on exit.

        Example::

            with config.overlay({"debug": True}):
                assert config.debug is True
            assert config.debug is False
        """
        originals: Dict[str, Any] = {}
        added_keys: List[str] = []

        for key, value in overrides.items():
            nk = self.__re(key)
            if nk in self.__dict__ and nk not in self.__protected_keys_:
                originals[nk] = self.__dict__[nk]
            else:
                added_keys.append(nk)
            self[key] = value

        try:
            yield self
        finally:
            for k, v in originals.items():
                self.__dict__[k] = v
            for k in added_keys:
                self.__dict__.pop(k, None)

    # JSON Serialization Methods

    def to_json(
        self,
        indent: Optional[int] = 2,
        sort_keys: bool = False,
        ensure_ascii: bool = True,
        **kwargs: Any,
    ) -> str:
        """Convert recursivenamespace to JSON string.

        Args:
            indent: Number of spaces for indentation (None for compact)
            sort_keys: Sort keys alphabetically
            ensure_ascii: Escape non-ASCII characters
            **kwargs: Additional arguments passed to json.dumps()

        Returns:
            str: JSON string representation

        Raises:
            SerializationError: If serialization fails
        """
        try:
            return json.dumps(
                self.to_dict(),
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii,
                **kwargs,
            )
        except (TypeError, ValueError) as e:
            raise SerializationError(f"Failed to serialize to JSON: {e}")

    @classmethod
    def from_json(
        cls,
        json_str: str,
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> "recursivenamespace":
        """Create recursivenamespace from JSON string.

        Args:
            json_str: JSON string to parse
            accepted_iter_types: Custom iterable types to preserve
            use_raw_key: Disable key normalization

        Returns:
            recursivenamespace: New namespace instance

        Raises:
            SerializationError: If deserialization fails
        """
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

    def save_json(
        self,
        filepath: Union[str, Path],
        indent: Optional[int] = 2,
        **kwargs: Any,
    ) -> None:
        """Save recursivenamespace to JSON file.

        Args:
            filepath: Path to output file
            indent: Number of spaces for indentation
            **kwargs: Additional arguments passed to to_json()

        Raises:
            SerializationError: If save fails
            IOError: If file cannot be written
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.to_json(indent=indent, **kwargs))
        except Exception as e:
            raise SerializationError(f"Failed to save JSON file: {e}")

    @classmethod
    def load_json(
        cls,
        filepath: Union[str, Path],
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> "recursivenamespace":
        """Load recursivenamespace from JSON file.

        Args:
            filepath: Path to JSON file
            accepted_iter_types: Custom iterable types to preserve
            use_raw_key: Disable key normalization

        Returns:
            recursivenamespace: New namespace instance

        Raises:
            SerializationError: If load fails
            FileNotFoundError: If file doesn't exist
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return cls.from_json(f.read(), accepted_iter_types, use_raw_key)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise SerializationError(f"Failed to load JSON file: {e}")

    # TODO(refactor): reduce cognitive complexity (~19) — 5-level nested type checks for TOML
    @staticmethod
    def _dict_to_toml(data: Dict[str, Any], prefix: str = "") -> str:
        """Convert dict to TOML format.

        Supports basic types: str, int, float, bool, list, dict.
        Does NOT support: datetime, inline tables, complex nesting in arrays.
        """
        lines = []
        simple_values = []
        tables = []

        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                tables.append((full_key, value))
            elif isinstance(value, (str, int, float, bool, type(None))):
                if isinstance(value, str):
                    # Escape special characters in strings
                    value = value.replace("\\", "\\\\").replace('"', '\\"')
                    simple_values.append(f'{key} = "{value}"')
                elif isinstance(value, bool):
                    simple_values.append(f"{key} = {str(value).lower()}")
                elif value is None:
                    # TOML doesn't have null, skip
                    continue
                else:
                    simple_values.append(f"{key} = {value}")
            elif isinstance(value, (list, tuple)):
                # Simple array handling (only primitive types)
                if all(isinstance(v, (str, int, float, bool)) for v in value):
                    array_str = "["
                    for v in value:
                        if isinstance(v, str):
                            v = v.replace("\\", "\\\\").replace('"', '\\"')
                            array_str += f'"{v}", '
                        elif isinstance(v, bool):
                            array_str += f"{str(v).lower()}, "
                        else:
                            array_str += f"{v}, "
                    if len(value) > 0:
                        array_str = array_str[:-2]  # Remove last comma
                    array_str += "]"
                    simple_values.append(f"{key} = {array_str}")
                else:
                    # Complex arrays not fully supported
                    simple_values.append(
                        f"# {key} = [complex array - not serialized]"
                    )
            else:
                simple_values.append(
                    f"# {key} = [type {type(value).__name__} not supported]"
                )

        # Write simple values first
        if simple_values:
            lines.extend(simple_values)

        # Write tables
        for table_key, table_value in tables:
            lines.append("")  # Empty line before table
            lines.append(f"[{table_key}]")
            table_content = recursivenamespace._dict_to_toml(table_value, "")
            lines.append(table_content)

        return "\n".join(lines)

    def to_toml(self) -> str:
        """Convert recursivenamespace to TOML string.

        Note: This is a minimal TOML writer supporting basic config types.
        Limitations:
        - No datetime support
        - Limited array nesting
        - No inline tables

        Returns:
            str: TOML string representation

        Raises:
            SerializationError: If serialization fails
        """
        try:
            return self._dict_to_toml(self.to_dict())
        except Exception as e:
            raise SerializationError(f"Failed to serialize to TOML: {e}")

    @classmethod
    def from_toml(
        cls,
        toml_str: str,
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> "recursivenamespace":
        """Create recursivenamespace from TOML string.

        Args:
            toml_str: TOML string to parse
            accepted_iter_types: Custom iterable types to preserve
            use_raw_key: Disable key normalization

        Returns:
            recursivenamespace: New namespace instance

        Raises:
            SerializationError: If deserialization fails
            ImportError: If tomllib not available
        """
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

    def save_toml(self, filepath: Union[str, Path]) -> None:
        """Save recursivenamespace to TOML file.

        Args:
            filepath: Path to output file

        Raises:
            SerializationError: If save fails
            IOError: If file cannot be written
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.to_toml())
        except Exception as e:
            raise SerializationError(f"Failed to save TOML file: {e}")

    @classmethod
    def load_toml(
        cls,
        filepath: Union[str, Path],
        accepted_iter_types: Optional[List[type]] = None,
        use_raw_key: bool = False,
    ) -> "recursivenamespace":
        """Load recursivenamespace from TOML file.

        Args:
            filepath: Path to TOML file
            accepted_iter_types: Custom iterable types to preserve
            use_raw_key: Disable key normalization

        Returns:
            recursivenamespace: New namespace instance

        Raises:
            SerializationError: If load fails
            FileNotFoundError: If file doesn't exist
            ImportError: If tomllib not available
        """
        if tomllib is None:
            raise ImportError(
                "TOML support requires Python 3.11+ or 'tomli' package. "
                "Install with: pip install tomli"
            )
        try:
            with open(filepath, "rb") as f:  # TOML requires binary mode
                data = tomllib.load(f)
                return cls(data, accepted_iter_types, use_raw_key)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise SerializationError(f"Failed to load TOML file: {e}")


# %%
# TODO(refactor): reduce cognitive complexity (~17) — multi-branch data type handling
def rns(
    accepted_iter_types: Optional[List[type]] = None,
    use_raw_key: bool = False,
    use_chain_key: bool = False,
    props: str = "props",
) -> Callable[[Callable[..., Any]], Callable[..., recursivenamespace]]:
    """Create RNS object"""
    if accepted_iter_types is None:
        accepted_iter_types_list: List[type] = []
    else:
        accepted_iter_types_list = accepted_iter_types

    def fn_wrapper(
        func: Callable[..., Any],
    ) -> Callable[..., recursivenamespace]:  # NOSONAR
        @functools.wraps(func)
        def create_rns(*args: Any, **kwargs: Any) -> recursivenamespace:
            # Do something before:
            ret_val = func(*args, **kwargs)

            # Prepare data:
            # create from kv_pair ??
            data: Any
            if (
                use_chain_key
                and isinstance(ret_val, list)
                and (len(ret_val) == 0 or isinstance(ret_val[0], utils.KV_Pair))
            ):
                data = ret_val
            elif isinstance(ret_val, dict):
                data = ret_val
            elif dataclasses.is_dataclass(ret_val):
                data = dataclasses.asdict(ret_val)  # type: ignore[arg-type]
            else:
                data = {f"{props}": ret_val}

            # Do something after:
            if use_chain_key:
                ret = recursivenamespace(
                    None, accepted_iter_types_list, use_raw_key
                )
                items = data.items() if isinstance(data, dict) else data
                for key, value in items:
                    ret.val_set(key, value)
                return ret
            else:
                return recursivenamespace(
                    data, accepted_iter_types_list, use_raw_key
                )

        return create_rns

    # @ret:
    return fn_wrapper
