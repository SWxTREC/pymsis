# NRL Mass Spectrometer, Incoherent Scatter Radar Extended Model (MSIS2)

The [model](
https://www.nrl.navy.mil/ssd/branches/7630/modeling-upper-atmosphere) was developed by the Naval Research Laboratory.

## References

Please acknowledge the University of Colorado Space Weather Technology, Research and Education Center (SWx TREC) and cite the original paper if you make use of this model.

> Picone, J. M., Hedin, A. E., Drob, D. P., and Aikin, A. C., NRLMSISE‐00 empirical model of the atmosphere: Statistical comparisons and scientific issues, J. Geophys. Res., 107( A12), 1468, [doi:10.1029/2002JA009430](https://doi.org/10.1029/2002JA009430), 2002.

## Installation

You have to get the source distribution from NRL, it will be in a tarfile called `NRLMSIS2.0.tar.gz`

### Preparing the Fortran source code

1. Extract the source code

    ```bash
    mkdir msis2
    tar -xvzf NRLMSIS2.0.tar.gz -C msis2/
    ```

2. Move the parameter file to the correct filename.

    ```bash
    mv msis2/msis20.parm msis2/msis2.0.parm
    ```

3. Remove bad UTF-8 characters from the source code comments

    ```bash
    sed -s -i '/^\s*!/d' msis2/*.F90
    ```

4. Remove the `^M` characters

    ```bash
    sed -s -i 's/^M//' msis2/*
    ```

### Python installation

To install `pymsis2` into your current environment is your typical python install procedure.

`pip install .`

or

`python setup.py install`
