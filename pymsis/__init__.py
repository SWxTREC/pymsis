import os
from pathlib import Path
__version__ = "0.5.0"

# If we are on Windows, Python 3.8+ then we need to add a DLL search path
# The libraries are located relative to this init file.
if os.name == 'nt':
    pymsis_dir = None
    pymsis_dir_libs = None
    try:
        # add folder to Windows DLL search paths
        pymsis_dir = Path(__file__).resolve().parent
        pymsis_dir_libs = pymsis_dir / '.libs'
        # This was added in Python 3.8, so we can default to this
        # once we only support 3.8+
        os.add_dll_directory(pymsis_dir)
        # Additionally, we need the .libs directory which has gfortran
        os.add_dll_directory(pymsis_dir_libs)

        os.environ['PATH'] = (f"{pymsis_dir};{pymsis_dir_libs};"
                              f"{os.environ['PATH']}")
    except Exception:
        pass
    del pymsis_dir, pymsis_dir_libs
