"""Python interface to the MSIS codes."""

import importlib.metadata

from pymsis.msis import Variable, calculate
from pymsis.utils import use_space_weather_file


__version__ = importlib.metadata.version("pymsis")

__all__ = ["Variable", "__version__", "calculate", "use_space_weather_file"]
