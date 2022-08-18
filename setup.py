#!/usr/bin/env python

"""The setup script."""
from pathlib import Path
import sys
from numpy.distutils.core import Extension, setup

# Some system's don't include the local directory on the
# base Python path for some reason, so add it in directly
sys.path.insert(0, str(Path.cwd()))
from pymsis import __version__
from tools.download_source import get_source


# Download and clean the source files
get_source()

# wrapper files
msis20_wrappers = [Path("src") / "wrappers" / x for x in ['msis20.pyf', 'msis2.F90']]
msis21_wrappers = [Path("src") / "wrappers" / x for x in ['msis21.pyf', 'msis2.F90']]
                  
# Explicit list of the Fortran filenames
msis20_sources = ['msis_constants.F90', 'msis_init.F90', 'msis_gfn.F90',
                  'msis_tfn.F90', 'alt2gph.F90', 'msis_dfn.F90',
                  'msis_calc.F90']
msis20_sources = [Path("src") / "msis2.0" / x for x in msis20_sources]
ext_msis20 = Extension(name='pymsis.msis20f',
                      sources=[str(x) for x in msis20_wrappers + msis20_sources], # [str(x) for x in msis2_wrappers + msis20_sources],
                      extra_f90_compile_args=['-std=legacy', '-O1'])

msis21_sources = ['msis_constants.F90', 'msis_init.F90', 'msis_gfn.F90',
                  'msis_utils.F90', 'msis_tfn.F90', 'msis_dfn.F90',
                  'msis_calc.F90']
# Add the directory where the files are located
msis21_sources = [Path("src") / "msis2.1" / x for x in msis21_sources]
# If you want to get some additional speed from compile-time options you can
# add extra compile-time flags. e.g., '-march=native', '-ffast-math'
# NOTE: -O1 seems to be required on Windows+Py39 CI systems, so we are setting
#       that for everyone for now, but it should be investigated later.
ext_msis21 = Extension(name='pymsis.msis21f',
                      sources=[str(x) for x in msis21_wrappers + msis21_sources],
                      extra_f90_compile_args=['-std=legacy', '-O1'])

msis00_sources = [Path('src/wrappers/msis00.F90'),
                  Path('src/msis00/NRLMSISE-00.FOR')]
ext_msis00 = Extension(name='pymsis.msis00f',
                       sources=[str(x) for x in msis00_sources],
                       extra_f77_compile_args=['-std=legacy'])

with open("README.rst", "r", encoding='utf8', errors="ignore") as f:
    long_description = f.read()

setup(
    author="Greg Lucas",
    author_email='greg.lucas@lasp.colorado.edu',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
    ],
    description="A Python wrapper around the NRLMSIS model.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://swxtrec.github.io/pymsis/",
    ext_modules=[ext_msis21, ext_msis20, ext_msis00],
    license="MIT license",
    keywords='MSIS2, NRLMSIS',
    name='pymsis',
    data_files=[('pymsis', [str(Path('pymsis/msis2.0.parm')), str(Path('pymsis/msis21.parm'))])],
    include_package_data=True,
    packages=['pymsis'],
    install_requires=["numpy"],
    version=__version__,
)
