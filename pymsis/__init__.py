"""Python interface to the MSIS codes."""

import importlib.metadata

from pymsis.msis import Variable, calculate
from pymsis.utils import set_space_weather_path


__version__ = importlib.metadata.version("pymsis")

__all__ = ["Variable", "__version__", "calculate", "set_space_weather_path"]
