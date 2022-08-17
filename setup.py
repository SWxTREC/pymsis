#!/usr/bin/env python

"""The setup script."""
import os
import sys
from setuptools import Extension, setup

# Some system's don't include the local directory on the
# base Python path for some reason, so add it in directly
sys.path.insert(0, os.getcwd())
from pymsis import __version__
from tools.download_source import get_source


# Download and clean the source files
get_source()

# Explicit list of the Fortran filenames
# Put the pyf file first in the list and add in our own wrapper
msis2_sources = ['msis2.pyf', 'msis2.F90',
                 'msis_constants.F90', 'msis_init.F90', 'msis_gfn.F90',
                 'msis_tfn.F90', 'alt2gph.F90', 'msis_dfn.F90',
                 'msis_calc.F90']
# Add the directory where the files are located
msis2_sources = [os.path.join('src', 'msis2', x) for x in msis2_sources]

# If you want to get some additional speed from compile-time options you can
# add extra compile-time flags. e.g., '-march=native', '-ffast-math'
# NOTE: -O1 seems to be required on Windows+Py39 CI systems, so we are setting
#       that for everyone for now, but it should be investigated later.
ext_msis2 = Extension(name='pymsis.msis2f',
                      sources=msis2_sources,
                      extra_f90_compile_args=['-std=legacy', '-O1'])

msis00_sources = [os.path.join('src', 'msis00', 'msis00.F90'),
                  os.path.join('src', 'msis00', 'NRLMSISE-00.FOR')]
ext_msis00 = Extension(name='pymsis.msis00f',
                       sources=msis00_sources,
                       extra_f77_compile_args=['-std=legacy'])

requirements = ['numpy']

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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="A Python wrapper around the NRLMSIS model.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://swxtrec.github.io/pymsis/",
    ext_modules=[ext_msis2, ext_msis00],
    license="MIT license",
    keywords='MSIS2, NRLMSIS',
    name='pymsis',
    data_files=[('pymsis', [os.path.join('pymsis', 'msis2.0.parm')])],
    include_package_data=True,
    packages=['pymsis'],
    install_requires=requirements,
    version=__version__,
)
