from pathlib import Path

import numpy as np

from pymsis import msis00f, msis20f, msis21f
from pymsis.utils import get_f107_ap


def run(
    dates,
    lons,
    lats,
    alts,
    f107s=None,
    f107as=None,
    aps=None,
    *,
    options=None,
    version=2.1,
    **kwargs,
):
    """
    Call MSIS looping over all possible inputs.

    If ndates is the same as nlons, nlats, and nalts, then a flattened
    multi-point input array is assumed. Otherwise, the data
    will be expanded in a grid-like fashion. The possible
    return shapes are therefore (ndates, 11) and
    (ndates, nlons, nlats, nalts, 11).

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
    f107s : list of floats, optional
        Daily F10.7 of the previous day for the given date(s)
    f107as : list of floats, optional
        F10.7 running 81-day average centered on the given date(s)
    aps : list of floats, optional
        | Ap for the given date(s), (1-6 only used if `geomagnetic_activity=-1`)
        | (0) Daily Ap
        | (1) 3 hr ap index for current time
        | (2) 3 hr ap index for 3 hrs before current time
        | (3) 3 hr ap index for 6 hrs before current time
        | (4) 3 hr ap index for 9 hrs before current time
        | (5) Average of eight 3 hr ap indices from 12 to 33 hrs
        |     prior to current time
        | (6) Average of eight 3 hr ap indices from 36 to 57 hrs
        |     prior to current time
    options : list of floats (length 25) [optional]
        A list of options (switches) to the model, if options is passed
        all keyword arguments specifying individual options will be ignored.
    version : Number or string, default: 2.1
        MSIS version number, [0, 2.0, 2.1]

    Returns
    -------
    ndarray (ndates, nlons, nlats, nalts, 11) or (ndates, 11)
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
        | NO # density (m-3),
        | Temperature (K)]

    Other Parameters
    ----------------
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

    Notes
    -----
    1. The 10.7 cm radio flux is at the Sun-Earth distance,
       not the radio flux at 1 AU.
    2. aps[1:] are only used when ``geomagnetic_activity=-1``.

    """
    if options is None:
        options = create_options(**kwargs)
    elif len(options) != 25:
        raise ValueError("options needs to be a list of length 25")

    input_shape, input_data = create_input(dates, lons, lats, alts, f107s, f107as, aps)

    if np.any(~np.isfinite(input_data)):
        raise ValueError(
            "Input data has non-finite values, all input data must be valid."
        )

    # convert to string version
    version = str(version)
    if version in {"0", "00"}:
        msis00f.pytselec(options)
        output = msis00f.pygtd7d(
            input_data[:, 0],
            input_data[:, 1],
            input_data[:, 2],
            input_data[:, 3],
            input_data[:, 4],
            input_data[:, 5],
            input_data[:, 6],
            input_data[:, 7:],
        )

    elif version.startswith("2"):
        # We need to point to the MSIS parameter file that was installed with
        # the Python package
        msis_path = str(Path(__file__).resolve().parent) + "/"

        # Select the proper library. Default to version 2.1, unless explicitly
        # requested "2.0" via string
        msis_lib = msis21f
        if version == "2.0":
            msis_lib = msis20f
        msis_lib.pyinitswitch(options, parmpath=msis_path)
        output = msis_lib.pymsiscalc(
            input_data[:, 0],
            input_data[:, 1],
            input_data[:, 2],
            input_data[:, 3],
            input_data[:, 4],
            input_data[:, 5],
            input_data[:, 6],
            input_data[:, 7:],
        )

    else:
        raise ValueError(
            f"The MSIS version selected: {version} is not "
            "a valid version number [0, 2]"
        )

    # The Fortran code puts 9.9e-38 in as NaN
    # Have to make sure this doesn't overlap 0 due to really small values
    # so atol should be less than the comparison value
    output[np.isclose(output, 9.9e-38, atol=1e-38)] = np.nan

    return output.reshape(input_shape + (11,))


def create_options(
    f107=1,
    time_independent=1,
    symmetrical_annual=1,
    symmetrical_semiannual=1,
    asymmetrical_annual=1,
    asymmetrical_semiannual=1,
    diurnal=1,
    semidiurnal=1,
    geomagnetic_activity=1,
    all_ut_effects=1,
    longitudinal=1,
    mixed_ut_long=1,
    mixed_ap_ut_long=1,
    terdiurnal=1,
):
    """
    Create the options list based on keyword argument choices.

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
    options = [
        f107,
        time_independent,
        symmetrical_annual,
        symmetrical_semiannual,
        asymmetrical_annual,
        asymmetrical_semiannual,
        diurnal,
        semidiurnal,
        geomagnetic_activity,
        all_ut_effects,
        longitudinal,
        mixed_ut_long,
        mixed_ap_ut_long,
        terdiurnal,
    ] + [1] * 11
    return options


def create_input(dates, lons, lats, alts, f107s=None, f107as=None, aps=None):
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
    f107s : list of floats, optional
        F107 values for the previous day of the given date(s)
    f107as : list of floats, optional
        F107 running 81-day average for the given date(s)
    aps : list of floats, optional
        Ap for the given date(s)

    Returns
    -------
    tuple (shape, flattened_input)
        The shape of the data as a tuple (ndates, nlons, nlats, nalts) and
        the flattened version of the input data
        (ndates*nlons*nlats*nalts, 14). If the input array was preflattened
        (ndates == nlons == nlats == nalts), then the shape is (ndates,).
    """
    # Turn everything into arrays
    dates = np.atleast_1d(np.array(dates, dtype="datetime64"))
    dyear = (dates.astype("datetime64[D]") - dates.astype("datetime64[Y]")).astype(
        float
    ) + 1  # DOY 1-366
    dseconds = (dates.astype("datetime64[s]") - dates.astype("datetime64[D]")).astype(
        float
    )
    # TODO: Make it a continuous day of year?
    #       The new code mentions it should be and accepts float, but the
    #       regression tests indicate it should still be integer DOY
    # dyear += dseconds/86400
    lons = np.atleast_1d(lons)
    # If any longitudes were input as negatives, try to change them to
    # the (0, 360) range
    lons[lons < 0] += 360
    lats = np.atleast_1d(lats)
    alts = np.atleast_1d(alts)

    # If any of the geomagnetic data wasn't specified, we will default
    # to getting it with the utility functions.
    if f107s is None or f107as is None or aps is None:
        data = get_f107_ap(dates)
        # Only update the values that were None
        if f107s is None:
            f107s = data[0]
        if f107as is None:
            f107as = data[1]
        if aps is None:
            aps = data[2]

    f107s = np.atleast_1d(f107s)
    f107as = np.atleast_1d(f107as)
    aps = np.atleast_1d(aps)

    ndates = len(dates)
    nlons = len(lons)
    nlats = len(lats)
    nalts = len(alts)

    if not (ndates == len(f107s) == len(f107as) == len(aps)):
        raise ValueError(
            f"The length of dates ({ndates}), f107s "
            f"({len(f107s)}), f107as ({len(f107as)}), "
            f"and aps ({len(aps)}) must all be equal"
        )

    if ndates == nlons == nlats == nalts:
        # This means the data came in preflattened, from a satellite
        # trajectory for example, where we don't want to make a grid
        # out of the input data, we just want to stack it together.
        arr = np.stack([dyear, dseconds, lons, lats, alts, f107s, f107as], -1)

        # ap has 7 components, so we need to concatenate it onto the
        # arrays rather than stack
        flattened_input = np.concatenate([arr, aps], axis=1, dtype=np.float32)
        shape = (ndates,)
        return shape, flattened_input

    # Make a grid of indices
    indices = np.stack(
        np.meshgrid(
            np.arange(ndates),
            np.arange(nlons),
            np.arange(nlats),
            np.arange(nalts),
            indexing="ij",
        ),
        -1,
    ).reshape(-1, 4)

    # Now stack all of the arrays, indexing by the proper indices
    arr = np.stack(
        [
            dyear[indices[:, 0]],
            dseconds[indices[:, 0]],
            lons[indices[:, 1]],
            lats[indices[:, 2]],
            alts[indices[:, 3]],
            f107s[indices[:, 0]],
            f107as[indices[:, 0]],
        ],
        -1,
    )
    # ap has 7 components, so we need to concatenate it onto the
    # arrays rather than stack
    flattened_input = np.concatenate(
        [arr, aps[indices[:, 0], :]], axis=1, dtype=np.float32
    )
    shape = (ndates, nlons, nlats, nalts)
    return shape, flattened_input
