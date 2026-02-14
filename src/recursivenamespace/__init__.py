from __future__ import annotations

from .main import recursivenamespace
from .main import recursivenamespace as RecursiveNamespace
from .main import recursivenamespace as RNS
from . import main as rns
from .main import SerializationError

from importlib.metadata import version as _get_version

__version__: str = _get_version("RecursiveNamespaceV2")
del _get_version

__all__ = [
    "recursivenamespace",
    "RecursiveNamespace",
    "RNS",
    "rns",
    "SerializationError",
    "__version__",
]
