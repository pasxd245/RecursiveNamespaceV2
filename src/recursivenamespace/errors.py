"""Custom exception classes for RecursiveNamespaceV2."""

from __future__ import annotations

from typing import Any


class SetChainKeyError(KeyError):
    def __init__(self, obj: Any, key: str, sub_key: str) -> None:
        super().__init__(
            f"The object '{key}' typeof({type(obj)}) does not support"
            f" set[] operator on chain-key '{sub_key}'."
        )


class GetChainKeyError(KeyError):
    def __init__(self, obj: Any, key: str, sub_key: str) -> None:
        super().__init__(
            f"The object '{key}' typeof({type(obj)}) does not support"
            f" get[] operator on chain-key '{sub_key}'."
        )


class SerializationError(Exception):
    """Raised when serialization or deserialization fails."""

    pass
