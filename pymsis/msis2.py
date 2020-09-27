import os

import numpy as np

from . import msis2f


def run(dates, lons, lats, alts, f107s, f107as, aps, options=None):
    """Call MSIS looping over all possible inputs.

    Parameters
    ----------
    dates : list of dates
        Dates and times of interest
    lons : list of floats
        Longitudes of interest
    lats : list of floats
        Latitudes of interest
    alts : list of floats
        Altitudes of interest
    f107s : list of floats
        F107 value for the given date(s)
    f107as : list of floats
        F107 running 100-day average for the given date(s)
    aps : list of floats
        Ap for the given date(s)
    options : list of floats (length 25) [optional]
        A list of options (switches) to the model

    Returns
    -------
    ndarray (ndates, nlons, nlats, nalts, 11)
        | The data calculated at each grid point:
        | [Total mass density (kg/m3)
        | N2 # density (m-3),
        | O2 # density (m-3),
        | O # density (m-3),
        | He # density (m-3),
        | H # density (m-3),
        | Ar # density (m-3),
        | N # density (m-3),
        | Anomalous oxygen # density (m-3),
        | empty (will contain NO in future release),
        | Temperature (K)]

    Notes
    -----
    The 10.7 cm radio flux is at the Sun-Earth distance,
    not the radio flux at 1 AU.

    """
    if options is None:
        options = create_options()
    elif len(options) != 25:
        raise ValueError("options needs to be a list of length 25")

    # We need to point to the MSIS parameter file that was installed with
    # the Python package
    msis_path = os.path.dirname(os.path.realpath(__file__)) + "/"
    msis2f.pyinitswitch(options, parmpath=msis_path)

    input_shape, input_data = create_input(dates, lons, lats, alts,
                                           f107s, f107as, aps)

    output = msis2f.pymsiscalc(input_data[:, 0], input_data[:, 1],
                               input_data[:, 2], input_data[:, 3],
                               input_data[:, 4], input_data[:, 5],
                               input_data[:, 6], input_data[:, 7:])
    # The Fortran code puts 9.9e-38 in as NaN
    # Have to make sure this doesn't overlap 0 due to really small values
    # so atol should be less than the comparison value
    output[np.isclose(output, 9.9e-38, atol=1e-38)] = np.nan

    return output.reshape(input_shape + (11,))


def create_options(f107=1, time_independent=1, symmetrical_annual=1,
                   symmetrical_semiannual=1, asymmetrical_annual=1,
                   asymmetrical_semiannual=1, diurnal=1, semidiurnal=1,
                   geomagnetic_activity=1, all_ut_effects=1, longitudinal=1,
                   mixed_ut_long=1, mixed_ap_ut_long=1, terdiurnal=1):
    """Creates the options list based on keyword argument choices.

    Defaults to all 1's for the input options.

    Parameters
    ----------
    f107 : float
        Account for F10.7 variations
    time_independent : float
        Account for time variations
    symmetrical_annual : float
        Account for symmetrical annual variations
    symmetrical_semiannual : float
        Account for symmetrical semiannual variations
    asymmetrical_annual : float
        Account for asymmetrical annual variations
    asymmetrical_semiannual : float
        Account for asymmetrical semiannual variations
    diurnal : float
        Account for diurnal variations
    semidiurnal : float
        Account for semidiurnal variations
    geomagnetic_activity : float
        Account for geomagnetic activity
        (1 = Daily Ap mode, -1 = Storm-time Ap mode)
    all_ut_effects : float
        Account for all UT/longitudinal effects
    longitudinal : float
        Account for longitudinal effects
    mixed_ut_long : float
        Account for UT and mixed UT/longitudinal effects
    mixed_ap_ut_long : float
        Account for mixed Ap, UT, and longitudinal effects
    terdiurnal : float
        Account for terdiurnal variations

    Returns
    -------
    list
        25 options as a list ready for msis2 input
    """
    options = [f107, time_independent, symmetrical_annual,
               symmetrical_semiannual, asymmetrical_annual,
               asymmetrical_semiannual, diurnal, semidiurnal,
               geomagnetic_activity, all_ut_effects, longitudinal,
               mixed_ut_long, mixed_ap_ut_long, terdiurnal] + [1]*11
    return options


def create_input(dates, lons, lats, alts, f107s, f107as, aps):
    """Combine all input values into a single flattened array.

    Parameters
    ----------
    dates : list of dates
        Dates and times of interest
    lons : list of floats
        Longitudes of interest
    lats : list of floats
        Latitudes of interest
    alts : list of floats
        Altitudes of interest
    f107s : list of floats
        F107 values for the given date(s)
    f107as : list of floats
        F107 running 100-day average for the given date(s)
    aps : list of floats
        Ap for the given date(s)

    Returns
    -------
    (shape, flattened_input)
        The shape of the data as a tuple (ndates, nlons, nlats, nalts) and
        the flattened version of the input data
        (ndates*nlons*nlats*nalts, 14).
    """
    # Turn everything into arrays
    dates = np.atleast_1d(np.array(dates, dtype='datetime64'))
    dyear = (dates.astype('datetime64[D]') -
             dates.astype('datetime64[Y]')).astype(float) + 1  # DOY 1-366
    dseconds = (dates.astype('datetime64[s]') -
                dates.astype('datetime64[D]')).astype(float)
    # Make it a continuous day of year
    dyear += dseconds/86400
    lons = np.atleast_1d(lons)
    # If any longitudes were input as negatives, try to change them to
    # the (0, 360) range
    lons[lons < 0] += 360
    lats = np.atleast_1d(lats)
    alts = np.atleast_1d(alts)
    f107s = np.atleast_1d(f107s)
    f107as = np.atleast_1d(f107as)
    aps = np.atleast_1d(aps)

    ndates = len(dates)
    nlons = len(lons)
    nlats = len(lats)
    nalts = len(alts)
    shape = (ndates, nlons, nlats, nalts)

    if not (ndates == len(f107s) == len(f107as) == len(aps)):
        raise ValueError(f"The length of dates ({ndates}), f107s "
                         f"({len(f107s)}), f107as ({len(f107as)}), "
                         f"and aps ({len(aps)}) must all be equal")

    # Make a grid of indices
    indices = np.stack(np.meshgrid(np.arange(ndates),
                                   np.arange(nlons),
                                   np.arange(nlats),
                                   np.arange(nalts), indexing='ij'),
                       -1).reshape(-1, 4)

    # Now stack all of the arrays, indexing by the proper indices
    arr = np.stack([dyear[indices[:, 0]], dseconds[indices[:, 0]],
                    lons[indices[:, 1]], lats[indices[:, 2]],
                    alts[indices[:, 3]],
                    f107s[indices[:, 0]], f107as[indices[:, 0]]], -1)
    # ap has 7 components, so we need to concatenate it onto the
    # arrays rather than stack
    return shape, np.concatenate([arr, aps[indices[:, 0], :]], axis=1)
