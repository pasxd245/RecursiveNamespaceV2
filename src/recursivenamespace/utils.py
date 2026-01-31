from __future__ import annotations

from collections import OrderedDict
from enum import Enum
import re
from typing import Any, Dict, List, NamedTuple, Union


KEY_SEP_CHAR = "."
KEY_ARRAY = "[]"


def escape_key(key: str, sep: str | None = None) -> str:
    sep = sep or KEY_SEP_CHAR
    escape_char = rf"\\{sep}"
    return key.replace(sep, escape_char)


def unescape_key(key: str, sep: str | None = None) -> str:
    sep = sep or KEY_SEP_CHAR
    escape_char = rf"\\{sep}"
    return key.replace(escape_char, sep)


def split_key(key: str, sep: str | None = None) -> list[str]:
    sep = sep or KEY_SEP_CHAR
    s = rf"(?<!\\)\{sep}"
    p = re.compile(s)
    return re.split(p, key)


def join_key(parts: List[str], sep: str | None = None) -> str:
    sep = sep or KEY_SEP_CHAR
    return sep.join(parts)


class KV_Pair(NamedTuple):
    key: str
    value: Any


class FlatListType(Enum):
    SKIP = 0
    WITH_INDEX = 1
    WITHOUT_INDEX = 2
    WITH_SMART_INDEX = 3


def flatten_as_dict(
    data: Dict[str, Any] | None,
    sep: str = KEY_SEP_CHAR,
    flat_list: bool = False,
    use_ordered_dict: bool = True,
) -> Dict[str, Any]:
    out: Dict[str, Any] = OrderedDict() if use_ordered_dict else dict()
    sep_len = len(sep)

    def flatten(obj: Any, name: str = "") -> None:
        if isinstance(obj, dict):
            for attr in obj:
                flatten(obj[attr], f"{name}{escape_key(attr)}{sep}")
        elif flat_list and isinstance(obj, list):
            parent_name = f"{name[:-sep_len]}{KEY_ARRAY}{sep}"
            # use OrderedDict to retain the order, should not use index,
            # the index is considered as a "key" to differentiate:
            for i in range(len(obj)):
                key = f"{parent_name}{i}{sep}"
                flatten(obj[i], key)
        else:
            key = name[:-sep_len]
            out[key] = obj

    if data:
        flatten(data)
    # @ret:
    return out


def flatten_as_list(
    data: Dict[str, Any] | None,
    sep: str = KEY_SEP_CHAR,
    flat_list_type: FlatListType = FlatListType.SKIP,
) -> List[KV_Pair]:
    out: List[KV_Pair] = []
    out_keys: Dict[str | None, int] = {}
    out_ref_keys: Dict[str, str] = {}
    sep_len = len(sep)
    flat_list = flat_list_type in [
        FlatListType.WITH_INDEX,
        FlatListType.WITHOUT_INDEX,
        FlatListType.WITH_SMART_INDEX,
    ]

    def flatten(obj: Any, name: str = "", ref_name: str | None = None) -> None:
        if isinstance(obj, dict):
            for attr in obj:
                key = f"{name}{escape_key(attr)}{sep}"
                # print("1.0", [key, ref_name])
                flatten(obj[attr], key, ref_name)
        elif flat_list and isinstance(obj, list):
            # if ref_name is existing, means set the value to the last item of the array,
            # thus, the parent must refer "-1" (instead of "#" -> append):
            if ref_name is None or ref_name not in out_keys:
                parent_name = f"{name[:-sep_len]}{KEY_ARRAY}{sep}"
            else:
                t_key = out_ref_keys[ref_name]
                t_len = len(t_key) - 1  # -1 : exclude the sign "-".
                t_key += name[t_len:]
                parent_name = f"{t_key[:-sep_len]}{KEY_ARRAY}{sep}"
            # use the ordered in out-List to retain the order, should not use index,
            # the index is considered as a "key" to differentiate:
            if flat_list_type == FlatListType.WITH_INDEX:
                # all "indexes" will be added to output keys:
                for i in range(len(obj)):
                    key = f"{parent_name}{i}{sep}"
                    # print("2.1", [key, ref_name])
                    flatten(obj[i], key, ref_name)
            elif flat_list_type == FlatListType.WITHOUT_INDEX:
                # all "indexes" will be replaced by "#":
                for i in range(len(obj)):
                    key = f"{parent_name}#{sep}"
                    # print("2.2", [key, ref_name])
                    flatten(obj[i], key, ref_name)
            else:  # WITH_SMART_INDEX:
                # all "indexes" will be replaced by (same length):
                #  - "#" if append to end of the array
                #  - "-1" set value to last item of the array
                for i in range(len(obj)):
                    key = f"{parent_name}#{sep}"
                    ref_key = f"{parent_name}{i}{sep}"
                    # <-- last item.
                    out_ref_keys[ref_key] = f"{parent_name}-1{sep}"
                    # print("2.3", [key, ref_key])
                    flatten(obj[i], key, ref_key)
        else:
            key = name[:-sep_len]
            if ref_name not in out_keys:
                out_keys[ref_name] = 1
            # print("3.0", [key, ref_name])
            # add to result:
            out.append(KV_Pair(key, obj))

    if data:
        flatten(data)
    # @ret:
    return out
