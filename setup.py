#!/usr/bin/env python

"""The setup script."""
from numpy.distutils.core import Extension, setup

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
msis2_sources = ['src/msis2/' + x for x in msis2_sources]

ext_msis2 = Extension(name='pymsis.msis2f',
                      sources=msis2_sources,
                      extra_f90_compile_args=['-march=native', '-ffast-math'])

msis00_sources = ['src/msis00/msis00.F90', 'src/msis00/NRLMSISE-00.FOR']
ext_msis00 = Extension(name='pymsis.msis00f',
                       sources=msis00_sources,
                       extra_f77_compile_args=['-std=legacy'])

requirements = ['numpy']

setup(
    author="Greg Lucas",
    author_email='greg.lucas@lasp.colorado.edu',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A Python package for calling the MSIS2 Fortran code.",
    ext_modules=[ext_msis2, ext_msis00],
    license="MIT license",
    keywords='MSIS2, NRLMSIS',
    name='pymsis',
    data_files=[('pymsis', ['pymsis/msis2.0.parm'])],
    include_package_data=True,
    packages=['pymsis'],
    version='0.1.0',
    install_requires=requirements,
)
