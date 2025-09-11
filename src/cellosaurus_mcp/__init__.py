from importlib.metadata import version

from cellosaurus_mcp.main import run_app
from cellosaurus_mcp.mcp import mcp

__version__ = version("cellosaurus_mcp")

__all__ = ["mcp", "run_app", "__version__"]


if __name__ == "__main__":
    run_app()
