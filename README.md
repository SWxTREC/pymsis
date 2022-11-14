# pymsis: A python wrapper of the NRLMSIS model

![image](https://swxtrec.github.io/pymsis/_static/pymsis-logo.png)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5348502.svg)](https://doi.org/10.5281/zenodo.5348502)
![PyPi](https://badge.fury.io/py/pymsis.svg)
![Downloads](https://pepy.tech/badge/pymsis/month)
![GitHubActions](https://github.com/SWxTREC/pymsis/actions/workflows/tests.yml/badge.svg)

Pymsis is meant to be a minimal and fast Python wrapper of the NRLMSIS
models. Documentation to get started quickly can be found on the [home
page](https://swxtrec.github.io/pymsis/). It includes some
[examples](https://swxtrec.github.io/pymsis/examples/index.html) that
demonstrate how to access and plot the data.

## Quickstart

A few short lines of code to get started quickly with pymsis.
Use Numpy to create a range of dates during the 2003 Halloween storm.
Then run the model at the location (lon, lat) (0, 0) and 400 km altitude.
The model will automatically download and access the F10.7 and ap data for you
if you have an internet connection.
The returned data structure has shape [ndates, nlons, nlats, nalts, 11],
but note that for this example we only have one longitude, latitude, and altitude.
The 11 is for each of the species MSIS calculates at each point of input.
The first element is the Total Mass Density (kg/m3) and if we plot that over
time, we can see how the mass density increased at 400 km altitude during this storm.

```python
import numpy as np
from pymsis import msis

dates = np.arange(np.datetime64("2003-10-28T00:00"), np.datetime64("2003-11-04T00:00"), np.timedelta64(30, "m"))
# geomagnetic_activity=-1 is a storm-time run
data = msis.run(dates, 0, 0, 400, geomagnetic_activity=-1)

# Plot the data
import matplotlib.pyplot as plt
# Total mass density over time
plt.plot(dates, data[:, 0, 0, 0, 0])
plt.tight_layout()
plt.show()
```

[Additional examples](https://swxtrec.github.io/pymsis/examples/index.html) that
demonstrate how to access and plot the data.

[API Documentation](https://swxtrec.github.io/pymsis/reference/index.html) with
details about the various options and configurations available.

## NRL Mass Spectrometer, Incoherent Scatter Radar Extended Model (MSIS)

The [MSIS
model](https://www.nrl.navy.mil/Our-Work/Areas-of-Research/Space-Science/)
is developed by the Naval Research Laboratory.

Note that the MSIS2 code is not available for commercial use without
contacting NRL. See the [MSIS2 license file](MSIS2_LICENSE) for explicit
details. We do not repackage the MSIS source code in this
repository for that reason. However, we do provide utilities to easily
download and extract the original source code. By using that code you
agree to their terms and conditions.

## References

Please acknowledge the University of Colorado Space Weather Technology,
Research and Education Center (SWx TREC) and cite the original papers if
you make use of this model in a publication.

### Python Code

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5348502.svg)](https://doi.org/10.5281/zenodo.5348502)

> Lucas, G. (2022). pymsis [Computer software]. [doi:10.5281/zenodo.5348502](https://doi.org/10.1029/2022JA030896)

### MSIS2.1

> Emmert, J. T., Jones, M., Siskind, D. E., Drob, D. P., Picone, J. M.,
> Stevens, M. H., et al. (2022). NRLMSIS 2.1: An empirical model of nitric
> oxide incorporated into MSIS. Journal of Geophysical Research: Space
> Physics, 127, e2022JA030896. [doi:10.1029/2022JA030896](https://doi.org/10.1029/2022JA030896)

### MSIS2.0

> Emmert, J. T., Drob, D. P., Picone, J. M., Siskind, D. E., Jones, M.,
> Mlynczak, M. G., et al. (2020). NRLMSIS 2.0: A whole‐atmosphere
> empirical model of temperature and neutral species densities. Earth
> and Space Science, 7, e2020EA001321.
> [doi:10.1029/2020EA001321](https://doi.org/10.1029/2020EA001321)

### MSISE-00

> Picone, J. M., Hedin, A. E., Drob, D. P., and Aikin, A. C.,
> NRLMSISE‐00 empirical model of the atmosphere: Statistical comparisons
> and scientific issues, J. Geophys. Res., 107( A12), 1468,
> [doi:10.1029/2002JA009430](https://doi.org/10.1029/2002JA009430),
> 2002.

### Geomagnetic Data

If you make use of the automatic downloads of the F10.7 and ap data,
please cite that data in your publication as well.

> Matzka, J., Stolle, C., Yamazaki, Y., Bronkalla, O. and Morschhauser, A.,
> 2021. The geomagnetic Kp index and derived indices of geomagnetic activity.
> Space Weather, [doi:10.1029/2020SW002641](https://doi.org/10.1029/2020SW002641).

## Installation

The easiest way to install pymsis is to install from PyPI.

``` bash
pip install pymsis
```

For the most up-to-date pymsis, you can install directly from the git
repository

``` bash
pip install git+https://github.com/SWxTREC/pymsis.git
```

or to work on it locally, you can clone the repository and install the
test dependencies.

``` bash
git clone https://github.com/SWxTREC/pymsis.git
cd pymsis
pip install .[tests]
```

### Remote installation

The installation is dependent on access to the NRL source code. If the
download fails, or you have no internet access you can manually install
the Fortran source code as follows.

1. **Download the source code**
    The source code is hosted on NRL\'s website:
    <https://map.nrl.navy.mil/map/pub/nrl/NRLMSIS/NRLMSIS2.0/>
    Download the `NRLMSIS2.0.tar.gz` file to your local system.

2. **Extract the source files**
    The tar file needs to be extracted to the `src/msis2.0` directory.

    ```bash
    tar -xvzf NRLMSIS2.0.tar.gz -C src/msis2.0/
    ```

3. **Install the Python package**

    ``` bash
    pip install .
    ```
