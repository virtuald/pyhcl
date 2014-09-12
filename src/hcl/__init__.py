
from .api import dumps, load, loads

try:
    from .version import __version__
except ImportError:
    __version__ = 'master'
