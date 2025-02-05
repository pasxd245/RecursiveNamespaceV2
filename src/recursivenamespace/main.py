#############################
# Fork: https://github.com/HessamLa/recursivenamespace
# %%
import dataclasses
import logging
import re
import sys
from typing import Any, List
from copy import deepcopy
from types import SimpleNamespace
import functools

from . import utils


__all__ = ["recursivenamespace"]


class SetChainKeyError(KeyError):
    def __init__(self, obj, key, sub_key):
        super().__init__(
            f"The object '{key}' typeof({type(obj)}) does not support set[] operator on chain-key '{sub_key}'."
        )


class GetChainKeyError(KeyError):
    def __init__(self, obj, key, sub_key):
        super().__init__(
            f"The object '{key}' typeof({type(obj)}) does not support get[] operator on chain-key '{sub_key}'."
        )


class recursivenamespace(SimpleNamespace):
    __HASH__ = "#"
    __logger = logging.getLogger(__name__)

    def __init__(
        self, data={}, accepted_iter_types=[], use_raw_key=False, **kwargs
    ):
        self.__key_ = ""
        self.__use_raw_key_ = use_raw_key
        self.__supported_types_ = list(
            dict.fromkeys([list, tuple, set] + accepted_iter_types)
        )

        self.__protected_keys_ = ()  # this to add the attr to __dict__.
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

    def __process(self, val, accepted_iter_types=[], use_raw_key=False):
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
                    out=sys.stderr,
                )
                return val
        else:
            return val

    def __re(self, key):
        return key if self.__use_raw_key_ else re.sub(r"[.\-\s]", "_", key)

    def set_key(self, key):
        self.__key_ = self.__re(key)

    def get_key(self):
        return self.__key_

    def update(self, data):
        try:
            if not isinstance(data, recursivenamespace):
                data = recursivenamespace(
                    data, self.__supported_types_, self.__use_raw_key_
                )
        except:
            raise Exception(f"Failed to update with data of type {type(data)}")
        for key, val in data.items():
            self[key] = val

    def __remove_protected_key(self, key):
        """Use with be-careful!"""
        self.__protected_keys_.remove(key)
        self.__dict__.pop(key)

    def __eq__(self, other):
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

    def __len__(self):
        return len(self.__dict__) - len(self.__protected_keys_)

    def __delattr__(self, key):
        key = self.__re(key)
        if key not in self.__protected_keys_:
            # delattr(self, key)
            del self.__dict__[key]

    def __setitem__(self, key: str, value: Any):
        key = self.__re(key)
        if key in self.__protected_keys_:
            raise KeyError(f"The key '{key}' is protected.")
        setattr(self, key, value)

    def __getitem__(self, key):
        key = self.__re(key)
        if key in self.__protected_keys_:
            raise KeyError(f"The key '{key}' is protected.")
        return getattr(self, key)

    def __delitem__(self, key):
        key = self.__re(key)
        delattr(self, key)

    def __contains__(self, key):
        key = self.__re(key)
        return key in self.__dict__

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def copy(self):
        return self.__copy__()

    def deepcopy(self):
        return self.__deepcopy__()

    def pop(self, key, default=None):
        key = self.__re(key)
        if key in self.__protected_keys_:
            raise KeyError(f"The key '{key}' is protected.")
        if key in self.__dict__:
            val = self.__dict__[key]
            del self.__dict__[key]
            return val
        else:
            return default

    def items(self):
        return [
            (k, v)
            for k, v in self.__dict__.items()
            if k not in self.__protected_keys_
        ]

    def keys(self):
        return [
            k for k in self.__dict__.keys() if k not in self.__protected_keys_
        ]

    def values(self):
        return [
            v
            for k, v in self.__dict__.items()
            if k not in self.__protected_keys_
        ]

    def __iter__(self):
        if sys._getframe(1).f_code.co_name == "dict":
            return self.to_dict()
        return iter(self.keys())

    def to_dict(self, flatten_sep: str = False):
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
            d = dict(utils.flatten_as_dict(d, sep=flatten_sep))
        return d

    def __iter_to_dict(self, iterable=None):
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

    def __chain_set_array(self, key, subs: List[str], value: any):
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

    def __chain_set_value(self, key, subs: List[str], value: any):
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

    def val_set(self, key: str, value: Any):
        """Set the value by key.
        Supported "chain-key", e.g.:
            - a.b.c <- set value to the item "c"
            - a.b.c[].<index-i> <- set value to the item at "index-i" of the array "c", same as: c[i] = value
            - a.b.c[].# <- append value to end of the array "c", same as: c.append(value)
            - a.b.c[].<index-i>.x[].<index-j> <- set value to the item at "index-j" of the array "x", same as: c[i].x[j] = value
            - a.b.c[].<index-i>.x[].# <- append value to end of the array "x", same as: c[i].x.append(value)
            - a.b.c[].#.x[].# <- append value to end of the new-array "x", same as:\n
                - new_item = RNS(dict(x=[])
                - new_item.x.append(value)
                - c.append(new_item)
            - ...

        Args:
            key (str): The key to set
            value (Any): The value to set

        Raises:
            KeyError: when try to set a protected value.
            SetChainKeyError: Only support chain-key on RNS type, else raise the error.
        """
        # raw_key = key
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

    def __chain_get_array(self, key, subs: List[str]):
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

    def __chain_get_value(self, key, subs: List[str]):
        target = self[key]
        sub_key = utils.join_key(subs)
        if isinstance(target, recursivenamespace):
            return target.val_get(sub_key)
        elif len(subs) == 1:
            return getattr(target, sub_key)
        else:
            raise GetChainKeyError(target, key, sub_key)

    def val_get(self, key: str):
        """Get the value by key.
        Supported "chain-key", e.g.:
            - a.b.c <- get the item "c"
            - a.b.c[].<index-i> <- get the item at "index-i" of the array "c"
            - a.b.c[].# <- get the last item of the array "c" (same as: -1)
            - a.b.c[].<index-i>.x[].<index-j> <- get the item at "index-j" of the array "x"
            - ...

        Args:
            key (str): The key to get

        Raises:
            KeyError: when try to get a protected value/or `key` is not existed.
            GetChainKeyError: Only support chain-key on RNS type, else raise the error.

        Returns:
            any: The value if the `key` is existed.
        """
        # raw_key = key
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

    def get_or_else(self, key: str, or_else=None, show_log=False):
        """Get the value by key.
        Supported "chain-key", e.g.: a.b.c

        Args:
            key (str): The key to get

        Returns:
            any: The value if the `key` is existed, else return `None`.
        """
        try:
            return self.val_get(key)
        except:
            # skip the error.
            if show_log:
                self.__logger.warning(f"KeyNotFound - {key}", exc_info=1)
            return or_else


# %%
def rns(
    accepted_iter_types=[],
    use_raw_key=False,
    use_chain_key=False,
    props="props",
):
    """Create RNS object"""

    def fn_wrapper(func):
        @functools.wraps(func)
        def create_rns(*args, **kwargs):
            # Do something before:
            ret_val = func(*args, **kwargs)

            # Prepare data:
            # create from kv_pair ??
            if (
                use_chain_key
                and isinstance(ret_val, list)
                and (len(ret_val) == 0 or isinstance(ret_val[0], utils.KV_Pair))
            ):
                data = ret_val
            elif isinstance(ret_val, dict):
                data = ret_val
            elif dataclasses.is_dataclass(ret_val):
                data = dataclasses.asdict(ret_val)
            else:
                data = {f"{props}": ret_val}

            # Do something after:
            if use_chain_key:
                ret = recursivenamespace(None, accepted_iter_types, use_raw_key)
                items = data.items() if isinstance(data, dict) else data
                for key, value in items:
                    ret.val_set(key, value)
                return ret
            else:
                return recursivenamespace(
                    data, accepted_iter_types, use_raw_key
                )

        return create_rns

    # @ret:
    return fn_wrapper
