"""Python interface to the MSIS codes."""

import importlib.metadata

from pymsis.msis import Variable, calculate


__version__ = importlib.metadata.version("pymsis")

__all__ = ["__version__", "Variable", "calculate"]
