from importlib.metadata import version

from cellosaurus_mcp.mcp import mcp
from cellosaurus_mcp.tools import *  # noqa: F403 import all tools to register them

__version__ = version("cellosaurus_mcp")

__all__ = ["mcp", "__version__"]
