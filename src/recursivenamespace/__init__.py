from .main import recursivenamespace
from .main import recursivenamespace as RecursiveNamespace
from .main import recursivenamespace as RNS
from . import main as rns

try:
    from recursivenamespace._version_pdm import (  # pyright: ignore [reportMissingImports]
        __version__,
    )
except ImportError:
    from recursivenamespace._version import get_versions

    __version__ = get_versions()["version"]
    del get_versions

__all__ = ["recursivenamespace", "RecursiveNamespace", "RNS", "rns"]
