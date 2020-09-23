import os

import numpy as np

from . import msis2f


def run(dates, lons, lats, alts, f107s, f107as, aps, options):
    """Call MSIS looping over all possible inputs.
    Parameters
    ----------
    dates : list of dates
        Date and time to calculate the output at.
    lons : list of floats
        Longitudes to calculate the output at.
    lats : list of floats
        Latitudes to calculate the output at.
    alts : list of floats
        Altitudes to calculate the output at.
    f107s : list of floats
        F107 value for the given date(s).
    f107as : list of floats
        F107 running 100-day average for the given date(s).
    aps : list of floats
        Ap for the given date(s).
    options : list of floats (length 25)
        A list of options (switches) to the model
    """
    # We need to point to the MSIS parameter file that was installed with
    # the Python package
    msis_path = os.path.dirname(os.path.realpath(__file__)) + "/"
    msis2f.pyinitswitch(options, parmpath=msis_path)

    input_data = create_input(dates, lons, lats, alts, f107s, f107as, aps)

    output = msis2f.pymsiscalc(input_data[:, 0], input_data[:, 1],
                               input_data[:, 2], input_data[:, 3],
                               input_data[:, 4], input_data[:, 5],
                               input_data[:, 6], input_data[:, 7:])

    # Force to float, JSON serializer in future calls does not work
    # with float32 output
    # Return the altitutdes, latitudes, longitudes with the data
    return (input_data[:, 2:5], output.astype(np.float))


def create_input(dates, lons, lats, alts, f107s, f107as, aps):
    """Combine all input values into a single flattened array."""
    # Turn everything into arrays
    dates = np.array(dates, dtype='datetime64')
    dyear = (dates.astype('datetime64[D]') -
             dates.astype('datetime64[Y]')).astype(float)
    dseconds = (dates.astype('datetime64[s]') -
                dates.astype('datetime64[D]')).astype(float)
    lons = np.array(lons)
    lats = np.array(lats)
    alts = np.array(alts)
    f107s = np.array(f107s)
    f107as = np.array(f107as)
    aps = np.array(aps)

    # Make a grid of indices
    indices = np.stack(np.meshgrid(np.arange(len(dates)),
                                   np.arange(len(lons)),
                                   np.arange(len(lats)),
                                   np.arange(len(alts))), -1).reshape(-1, 4)

    # Now stack all of the arrays, indexing by the proper indices
    arr = np.stack([dyear[indices[:, 0]], dseconds[indices[:, 0]],
                    lons[indices[:, 1]], lats[indices[:, 2]],
                    alts[indices[:, 3]],
                    f107s[indices[:, 0]], f107as[indices[:, 0]]], -1)
    # ap has 7 components, so we need to concatenate it onto the
    # arrays rather than stack
    return np.concatenate([arr, aps[indices[:, 0], :]], axis=1)


def example():

    alt = 200
    f107 = 146.7
    f107a = 163.6666
    ap = 7
    # One years worth of data at the 12th hour every day
    dates = np.arange('2003-01', '2004-01',
                      dtype='datetime64[D]') + np.timedelta64(12, 'h')
    ndates = len(dates)
    lons = range(-180, 185, 5)
    lats = range(-90, 95, 5)
    alts = [alt]
    # (F107, F107a, ap) all need to be specified at the same length as dates
    f107s = [f107]*ndates
    f107as = [f107a]*ndates
    aps = [[ap]*7]*ndates
    options = [0]*25

    output = run(dates, lons, lats, alts, f107s, f107as, aps, options)
    return output


if __name__ == "__main__":
    example()
