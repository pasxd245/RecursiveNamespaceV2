from .main import recursivenamespace
from .main import recursivenamespace as RecursiveNamespace
from .main import recursivenamespace as RNS
from . import main as rns

from . import _version

__all__ = ["recursivenamespace", "RecursiveNamespace", "RNS", "rns"]
__version__ = _version.get_versions()["version"]
