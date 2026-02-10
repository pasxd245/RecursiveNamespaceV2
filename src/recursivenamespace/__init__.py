from __future__ import annotations

from .main import recursivenamespace
from .main import recursivenamespace as RecursiveNamespace
from .main import recursivenamespace as RNS
from . import main as rns
from .main import SerializationError

from recursivenamespace._version import get_versions

__version__: str = get_versions()["version"]
del get_versions

__all__ = [
    "recursivenamespace",
    "RecursiveNamespace",
    "RNS",
    "rns",
    "SerializationError",
    "__version__",
]
