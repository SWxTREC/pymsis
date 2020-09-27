# pymsis: A python wrapper of the NRLMSIS model

Note that the MSIS2 code is not available for commercial use without contacting NRL.
See the [MSIS2 license file](MSIS2_LICENSE) for explicit details.
We do not repackage any of the source code
in the repository for this reason. However, we do provide utilities to easily download and extract the original source code. By using that code you agree to their terms and conditions.

## NRL Mass Spectrometer, Incoherent Scatter Radar Extended Model (MSIS)

The [MSIS model](
https://www.nrl.navy.mil/ssd/branches/7630/modeling-upper-atmosphere) is developed by the Naval Research Laboratory.

## References

Please acknowledge the University of Colorado Space Weather Technology, Research and Education Center (SWx TREC) and cite the original papers if you make use of this model in a publication.

> Emmert, J. T., Drob, D. P., Picone, J. M., Siskind, D. E., Jones, M., Mlynczak, M. G., et al. (2020). NRLMSIS 2.0: A whole‐atmosphere empirical model of temperature and neutral species densities. Earth and Space Science, 7, e2020EA001321. https://doi.org/10.1029/2020EA001321

The Original NRLMSISE-00 paper

> Picone, J. M., Hedin, A. E., Drob, D. P., and Aikin, A. C., NRLMSISE‐00 empirical model of the atmosphere: Statistical comparisons and scientific issues, J. Geophys. Res., 107( A12), 1468, [doi:10.1029/2002JA009430](https://doi.org/10.1029/2002JA009430), 2002.

## Installation

You can install pymsis from the git repository

```bash
pip install git+https://github.com/SWxTREC/pymsis.git
```

or to work on it locally, you can clone the repository and use an editable install

```bash
git clone https://github.com/SWxTREC/pymsis.git
pip install -e .
```

### Remote installation

The installation is dependent on access to the NRL source code. If the download fails,
of you have no internet access you can manually install the Fortran source code as follows.

1. **Download the source code**

    The source code is hosted on the NRL's website:
    [https://map.nrl.navy.mil/map/pub/nrl/NRLMSIS/NRLMSIS2.0/](https://map.nrl.navy.mil/map/pub/nrl/NRLMSIS/NRLMSIS2.0/)
    Download the `NRLMSIS2.0.tar.gz` file to your local system.

2. **Extract the source files**

    The tar file needs to be extracted to a new `msis2` directory in the base of the pymsis package.

    ```bash
    mkdir msis2
    tar -xvzf NRLMSIS2.0.tar.gz -C msis2/
    ```

3. **Install the Python package**

    ```bash
    pip install .
    ```
