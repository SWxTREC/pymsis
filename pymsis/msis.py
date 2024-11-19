"""Interface for running and creating input for the MSIS models."""

import threading
from enum import IntEnum
from pathlib import Path

import numpy as np
import numpy.typing as npt

from pymsis import msis00f, msis20f, msis21f  # type: ignore
from pymsis.utils import get_f107_ap


# We need to point to the MSIS parameter file that was installed with the Python package
_MSIS_PARAMETER_PATH = str(Path(__file__).resolve().parent) + "/"
for lib in [msis00f, msis20f, msis21f]:
    # Store the previous options to avoid reinitializing the model
    # each iteration unless necessary
    lib._last_used_options = None
    # Anytime we call into the Fortran code, we need to lock
    # to avoid threading issues
    lib._lock = threading.Lock()


class Variable(IntEnum):
    """
    Enumeration of output data indices for the pymsis run calls.

    This can be used to access the data from the output arrays instead of having
    to remember the order of the output. For example,
    ``output_array[..., Variable.MASS_DENSITY]``.

    Attributes
    ----------
    MASS_DENSITY
        Index of total mass density (kg/m3).
    N2
        Index of N2 number density (m-3).
    O2
        Index of O2 number density (m-3).
    O
        Index of O number density (m-3).
    HE
        Index of He number density (m-3).
    H
        Index of H number density (m-3).
    AR
        Index of Ar number density (m-3).
    N
        Index of N number density (m-3).
    ANOMALOUS_O
        Index of anomalous oxygen number density (m-3).
    NO
        Index of NO number density (m-3).
    TEMPERATURE
        Index of temperature (K).

    """

    MASS_DENSITY = 0
    N2 = 1
    O2 = 2
    O = 3  # noqa: E741 (ambiguous name)
    HE = 4
    H = 5
    AR = 6
    N = 7
    ANOMALOUS_O = 8
    NO = 9
    TEMPERATURE = 10


def run(
    dates: npt.ArrayLike,
    lons: npt.ArrayLike,
    lats: npt.ArrayLike,
    alts: npt.ArrayLike,
    f107s: npt.ArrayLike | None = None,
    f107as: npt.ArrayLike | None = None,
    aps: npt.ArrayLike | None = None,
    *,
    options: list[float] | None = None,
    version: float | str = 2.1,
    **kwargs: dict,
) -> npt.NDArray:
    """
    Call MSIS to calculate the atmosphere at the provided input points.

    **Satellite Fly-Through Mode:**
    If ndates is the same length as nlons, nlats, and nalts, then the
    input arrays are assumed to be aligned and no regridding is done.
    This is equivalent to a satellite fly-through, producing an output
    return shape of (ndates, 11).

    **Grid Mode:**
    If the input arrays have different lengths the data will be expanded
    in a grid-like fashion broadcasting to a larger shape than the input
    arrays. This is equivalent to a full atmosphere simulation where you
    want to calculate the data at every grid point. The output shape will
    be 5D (ndates, nlons, nlats, nalts, 11), with potentially single element
    dimensions if you have a single date, lon, lat, or alt.

    The output array can be indexed with the :class:`~.Variable` enum
    for easier access. ``output_array[..., Variable.MASS_DENSITY]``
    returns the total mass density.

    Parameters
    ----------
    dates : ArrayLike
        Dates and times of interest
    lons : ArrayLike
        Longitudes of interest
    lats : ArrayLike
        Latitudes of interest
    alts : ArrayLike
        Altitudes of interest
    f107s : ArrayLike, optional
        Daily F10.7 of the previous day for the given date(s)
    f107as : ArrayLike, optional
        F10.7 running 81-day average centered on the given date(s)
    aps : ArrayLike, optional
        | Ap for the given date(s), (1-6 only used if ``geomagnetic_activity=-1``)
        | (0) Daily Ap
        | (1) 3 hr ap index for current time
        | (2) 3 hr ap index for 3 hrs before current time
        | (3) 3 hr ap index for 6 hrs before current time
        | (4) 3 hr ap index for 9 hrs before current time
        | (5) Average of eight 3 hr ap indices from 12 to 33 hrs
        |     prior to current time
        | (6) Average of eight 3 hr ap indices from 36 to 57 hrs
        |     prior to current time
    options : ArrayLike[25, float], optional
        A list of options (switches) to the model, if options is passed
        all keyword arguments specifying individual options will be ignored.
    version : Number or string, default: 2.1
        MSIS version number, one of (0, 2.0, 2.1).
    **kwargs : dict
        Single options for the switches can be defined through keyword arguments.
        For example, run(..., geomagnetic_activity=-1) will set the geomagnetic
        activity switch to -1 (storm-time ap mode).

    Returns
    -------
    ndarray (ndates, nlons, nlats, nalts, 11) or (ndates, 11)
        | The data calculated at each grid point:
        | [Total mass density (kg/m3),
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
    num_options = 25
    if options is None:
        options = create_options(**kwargs)  # type: ignore
    elif len(options) != num_options:
        raise ValueError(f"options needs to be a list of length {num_options}")

    input_shape, input_data = create_input(dates, lons, lats, alts, f107s, f107as, aps)

    if np.any(~np.isfinite(input_data)):
        raise ValueError(
            "Input data has non-finite values, all input data must be valid."
        )

    # convert to string version
    version = str(version)
    # Select the underlying MSIS library based on the version
    match version:
        case "0" | "00":
            msis_lib = msis00f
        case "2.0":
            msis_lib = msis20f
        case "2.1" | "2":
            # generic 2 defaults to most recent available
            msis_lib = msis21f
        case _:
            raise ValueError(
                f"The MSIS version selected: {version} is not "
                "one of the valid version numbers: (0, 2.0, 2.1)"
            )

    with msis_lib._lock:
        # Only reinitialize the model if the options have changed
        if msis_lib._last_used_options != options:
            msis_lib.pyinitswitch(options, parmpath=_MSIS_PARAMETER_PATH)
            msis_lib._last_used_options = options

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

    # The Fortran code puts 9.9e-38 in as NaN
    # or 9.99e-38, or 9.999e-38, so lets just bound the 9s
    output[(output >= 9.9e-38) & (output < 1e-37)] = np.nan  # noqa: PLR2004

    return output.reshape(*input_shape, 11)


def create_options(
    f107: float = 1,
    time_independent: float = 1,
    symmetrical_annual: float = 1,
    symmetrical_semiannual: float = 1,
    asymmetrical_annual: float = 1,
    asymmetrical_semiannual: float = 1,
    diurnal: float = 1,
    semidiurnal: float = 1,
    geomagnetic_activity: float = 1,
    all_ut_effects: float = 1,
    longitudinal: float = 1,
    mixed_ut_long: float = 1,
    mixed_ap_ut_long: float = 1,
    terdiurnal: float = 1,
) -> list[float]:
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


def create_input(
    dates: npt.ArrayLike,
    lons: npt.ArrayLike,
    lats: npt.ArrayLike,
    alts: npt.ArrayLike,
    f107s: npt.ArrayLike | None = None,
    f107as: npt.ArrayLike | None = None,
    aps: npt.ArrayLike | None = None,
) -> tuple[tuple, npt.NDArray]:
    """
    Combine all input values into a single flattened array.

    Parameters
    ----------
    dates : ArrayLike
        Dates and times of interest
    lons : ArrayLike
        Longitudes of interest
    lats : ArrayLike
        Latitudes of interest
    alts : ArrayLike
        Altitudes of interest
    f107s : ArrayLike, optional
        F107 values for the previous day of the given date(s)
    f107as : ArrayLike, optional
        F107 running 81-day average for the given date(s)
    aps : ArrayLike, optional
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
    dates_arr: npt.NDArray[np.datetime64] = np.atleast_1d(
        np.array(dates, dtype=np.datetime64)
    )
    dyear: npt.NDArray[np.datetime64] = (
        dates_arr.astype("datetime64[D]") - dates_arr.astype("datetime64[Y]")
    ).astype(float) + 1  # DOY 1-366
    dseconds: npt.NDArray[np.datetime64] = (
        dates_arr.astype("datetime64[s]") - dates_arr.astype("datetime64[D]")
    ).astype(float)
    # TODO: Make it a continuous day of year?
    #       The new code mentions it should be and accepts float, but the
    #       regression tests indicate it should still be integer DOY
    # dyear += dseconds/86400
    lons = np.atleast_1d(lons)
    lats = np.atleast_1d(lats)
    alts = np.atleast_1d(alts)

    # If any of the geomagnetic data wasn't specified, we will default
    # to getting it with the utility functions.
    if f107s is None or f107as is None or aps is None:
        data = get_f107_ap(dates_arr)
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

    ndates = len(dates_arr)
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
        # Create an array to hold all of the data
        # F-ordering so we can pass by reference to the Fortran code
        arr = np.empty((ndates, 14), dtype=np.float32, order="F")
        arr[:, 0] = dyear
        arr[:, 1] = dseconds
        arr[:, 2] = lons
        arr[:, 3] = lats
        arr[:, 4] = alts
        arr[:, 5] = f107s
        arr[:, 6] = f107as
        arr[:, 7:] = aps
        return (ndates,), arr

    # Use broadcasting to fill each column directly
    # This is much faster than creating an indices array and then
    # using that to fill the columns
    arr = np.empty((ndates * nlons * nlats * nalts, 14), dtype=np.float32, order="F")
    arr[:, 0] = np.repeat(dyear, nlons * nlats * nalts)  # dyear
    arr[:, 1] = np.repeat(dseconds, nlons * nlats * nalts)  # dseconds
    arr[:, 2] = np.tile(np.repeat(lons, nlats * nalts), ndates)  # lons
    arr[:, 3] = np.tile(np.repeat(lats, nalts), ndates * nlons)  # lats
    arr[:, 4] = np.tile(alts, ndates * nlons * nlats)  # alts
    arr[:, 5] = np.repeat(f107s, nlons * nlats * nalts)  # f107s
    arr[:, 6] = np.repeat(f107as, nlons * nlats * nalts)  # f107as
    arr[:, 7:] = np.repeat(aps, nlons * nlats * nalts, axis=0)  # aps

    return (ndates, nlons, nlats, nalts), arr
