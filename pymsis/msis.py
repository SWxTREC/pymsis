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
    r"""
    Enumeration of variable data indices for the output from ``calculate()``.

    This can be used to access the data from the output arrays instead of having
    to remember the order of the output. For example,
    ``output_array[..., Variable.MASS_DENSITY]``.

    Attributes
    ----------
    MASS_DENSITY
        Index of total mass density (kg/m\ :sup:`3`).
    N2
        Index of N2 number density (m\ :sup:`-3`).
    O2
        Index of O2 number density (m\ :sup:`-3`).
    O
        Index of O number density (m\ :sup:`-3`).
    HE
        Index of He number density (m\ :sup:`-3`).
    H
        Index of H number density (m\ :sup:`-3`).
    AR
        Index of Ar number density (m\ :sup:`-3`).
    N
        Index of N number density (m\ :sup:`-3`).
    ANOMALOUS_O
        Index of anomalous oxygen number density (m\ :sup:`-3`).
    NO
        Index of NO number density (m\ :sup:`-3`).
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


def calculate(
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
    interpolate_indices: bool = False,
    **kwargs: dict,
) -> npt.NDArray:
    r"""
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

    If F10.7, F10.7a, or Ap values are not provided, the historical data
    for the given date(s) will be used. If the local file is not available,
    the data will be downloaded and cached for future use. See
    :func:`~pymsis.utils.get_f107_ap` for more details on the historical
    data retrieval.

    Parameters
    ----------
    dates : ArrayLike
        Dates and times of interest
    lons : ArrayLike
       Geodetic longitudes (deg), referenced to the WGS84 ellipsoid
    lats : ArrayLike
        Geodetic latitudes (deg), referenced to the WGS84 ellipsoid
    alts : ArrayLike
        Geodetic altitudes (km), referenced to the WGS84 ellipsoid
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
    interpolate_indices : bool, default: False
        If True, linearly interpolate F10.7, F10.7a, and ap indices between
        their native time resolution (daily for F10.7/F10.7a, 3-hourly for ap).
        If False (default), use step-function sampling where values change
        discretely at boundaries. Linear interpolation can provide smoother
        density variations for high-cadence simulations.
    **kwargs : dict
        Single options for the switches can be defined through keyword arguments.
        For example, ``calculate(..., geomagnetic_activity=-1)`` will set the
        geomagnetic activity switch to -1 (storm-time ap mode).

    Returns
    -------
    ndarray (ndates, nlons, nlats, nalts, 11) or (ndates, 11)
        | The data calculated at each grid point:
        | [Total mass density (kg/m\ :sup:`3`),
        | N2 # density (m\ :sup:`-3`),
        | O2 # density (m\ :sup:`-3`),
        | O # density (m\ :sup:`-3`),
        | He # density (m\ :sup:`-3`),
        | H # density (m\ :sup:`-3`),
        | Ar # density (m\ :sup:`-3`),
        | N # density (m\ :sup:`-3`),
        | Anomalous oxygen # density (m\ :sup:`-3`),
        | NO # density (m\ :sup:`-3`),
        | Temperature (K)]

    Other Parameters
    ----------------
    f107 : float
        Solar flux F10.7 effects on atmospheric density. Controls how much
        the current F10.7 value modifies the base atmospheric state. When set to 0,
        F10.7 variations are ignored and the atmosphere uses a standard reference
        solar flux level.
    time_independent : float
        Time-independent baseline atmospheric structure. Controls the
        basic north-south atmospheric variations that provide the fundamental
        geographic structure of the atmosphere independent of time. Setting
        to 0 removes these baseline latitude-dependent terms, leaving only
        time-varying atmospheric patterns.
    symmetrical_annual : float
        Annual variations that are the same in both hemispheres. Controls
        seasonal changes in atmospheric density due to Earth's orbit around
        the Sun. When set to 0, removes symmetric year-to-year variations.
    symmetrical_semiannual : float
        Semiannual (6-month) variations that are symmetric between hemispheres.
        Controls atmospheric changes that occur twice per year due to solar
        heating patterns. Setting to 0 removes these biannual variations.
    asymmetrical_annual : float
        Annual variations that differ between northern and southern hemispheres.
        Accounts for seasonal differences caused by land/ocean distribution and
        other hemispheric asymmetries. When set to 0, removes asymmetric
        seasonal effects.
    asymmetrical_semiannual : float
        Semiannual variations that differ between hemispheres. Controls
        atmospheric changes that occur twice yearly but with different magnitudes
        in each hemisphere. Setting to 0 removes these asymmetric biannual variations.
    diurnal : float
        Daily (24-hour) variations in atmospheric density. Controls day/night
        differences caused by solar heating and atmospheric tides. When set to 0,
        removes all diurnal atmospheric variations.
    semidiurnal : float
        Semi-daily (12-hour) variations in atmospheric density. Controls
        atmospheric tides that occur twice per day due to solar heating patterns.
        Setting to 0 removes these twice-daily atmospheric oscillations.
    geomagnetic_activity : float
        Geomagnetic activity effects on atmospheric heating and expansion.
        Controls how magnetic storms and aurora affect atmospheric density.
        (1 = Daily Ap mode using average daily values, -1 = Storm-time Ap mode
        using 3-hourly Ap indices for more detailed storm modeling)
    all_ut_effects : float
        Universal Time (UT) and longitudinal effects combined. Controls
        atmospheric variations that depend on the time of day in UT and
        geographic longitude. Setting to 0 removes all UT/longitude-dependent
        variations.
    longitudinal : float
        Pure longitudinal variations independent of UT. Controls atmospheric
        differences that vary only with geographic longitude (e.g., land/sea contrasts,
        topography). When set to 0, removes longitude-only atmospheric variations.
    mixed_ut_long : float
        Mixed Universal Time and longitudinal effects. Controls atmospheric
        variations that depend on both UT and longitude simultaneously (e.g.,
        regional differences in tidal patterns). Setting to 0 removes these
        coupled effects.
    mixed_ap_ut_long : float
        Combined geomagnetic activity, UT, and longitudinal effects. Controls
        how magnetic activity affects the atmosphere differently across longitude
        and UT. When set to 0, removes the geographic/temporal coupling of
        magnetic effects.
    terdiurnal : float
        Terdiurnal (8-hour) atmospheric variations. Controls atmospheric tides
        that occur three times per day due to solar heating harmonics. Setting
        to 0 removes these 8-hourly atmospheric oscillations.
    interpolate_indices : bool, default: False
        If True, linearly interpolate F10.7, F10.7a, and ap indices between
        their native time resolution (daily for F10.7/F10.7a, 3-hourly for ap).
        If False (default), use step-function sampling where values change
        discretely at boundaries. Linear interpolation can provide smoother
        density variations for high-cadence simulations.

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

    input_shape, input_data = create_input(
        dates,
        lons,
        lats,
        alts,
        f107s,
        f107as,
        aps,
        interpolate_indices=interpolate_indices,
    )

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


# For backwards compatibility export the old name here
run = calculate


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
    0 turns the option off.
    1 turns the option on.
    2 turns the main effects off, but the cross terms on.

    For geomagnetic_activity, 1 is for daily Ap mode, and -1 is for storm-time Ap mode.
    You may also use booleans for the options, ``diurnal=False`` will
    turn off the diurnal effect.

    Parameters
    ----------
    f107 : float
        Solar flux F10.7 effects on atmospheric density. Controls how much
        the current F10.7 value modifies the base atmospheric state. When set to 0,
        F10.7 variations are ignored and the atmosphere uses a standard reference
        solar flux level.
    time_independent : float
        Time-independent baseline atmospheric structure. Controls the
        basic north-south atmospheric variations that provide the fundamental
        geographic structure of the atmosphere independent of time. Setting
        to 0 removes these baseline latitude-dependent terms, leaving only
        time-varying atmospheric patterns.
    symmetrical_annual : float
        Annual variations that are the same in both hemispheres. Controls
        seasonal changes in atmospheric density due to Earth's orbit around
        the Sun. When set to 0, removes symmetric year-to-year variations.
    symmetrical_semiannual : float
        Semiannual (6-month) variations that are symmetric between hemispheres.
        Controls atmospheric changes that occur twice per year due to solar
        heating patterns. Setting to 0 removes these biannual variations.
    asymmetrical_annual : float
        Annual variations that differ between northern and southern hemispheres.
        Accounts for seasonal differences caused by land/ocean distribution and
        other hemispheric asymmetries. When set to 0, removes asymmetric
        seasonal effects.
    asymmetrical_semiannual : float
        Semiannual variations that differ between hemispheres. Controls
        atmospheric changes that occur twice yearly but with different magnitudes
        in each hemisphere. Setting to 0 removes these asymmetric biannual
        variations.
    diurnal : float
        Daily (24-hour) variations in atmospheric density. Controls day/night
        differences caused by solar heating and atmospheric tides. When set to 0,
        removes all diurnal atmospheric variations.
    semidiurnal : float
        Semi-daily (12-hour) variations in atmospheric density. Controls
        atmospheric tides that occur twice per day due to solar heating patterns.
        Setting to 0 removes these twice-daily atmospheric oscillations.
    geomagnetic_activity : float
        Geomagnetic activity effects on atmospheric heating and expansion.
        Controls how magnetic storms and aurora affect atmospheric density.
        (1 = Daily Ap mode using average daily values, -1 = Storm-time Ap mode
        using 3-hourly Ap indices for more detailed storm modeling)
    all_ut_effects : float
        Universal Time (UT) and longitudinal effects combined. Controls
        atmospheric variations that depend on the time of day in UT and
        geographic longitude. Setting to 0 removes all UT/longitude-dependent
        variations.
    longitudinal : float
        Pure longitudinal variations independent of UT. Controls atmospheric
        differences that vary only with geographic longitude (e.g., land/sea
        contrasts, topography). When set to 0, removes longitude-only
        atmospheric variations.
    mixed_ut_long : float
        Mixed Universal Time and longitudinal effects. Controls atmospheric
        variations that depend on both UT and longitude simultaneously (e.g.,
        regional differences in tidal patterns). Setting to 0 removes these
        coupled effects.
    mixed_ap_ut_long : float
        Combined geomagnetic activity, UT, and longitudinal effects. Controls
        how magnetic activity affects the atmosphere differently across longitude
        and UT. When set to 0, removes the geographic/temporal coupling of
        magnetic effects.
    terdiurnal : float
        Terdiurnal (8-hour) atmospheric variations. Controls atmospheric tides
        that occur three times per day due to solar heating harmonics. Setting
        to 0 removes these 8-hourly atmospheric oscillations.

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
    interpolate_indices: bool = False,
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
    interpolate_indices : bool, default: False
        If True, use linear interpolation for F10.7, F10.7a, and ap indices.
        If False, use step-function (nearest-neighbor) sampling.

    Returns
    -------
    tuple (shape, flattened_input)
        The shape of the data as a tuple (ndates, nlons, nlats, nalts) and
        the flattened version of the input data
        (ndates*nlons*nlats*nalts, 14). If the input array was preflattened
        (ndates == nlons == nlats == nalts), then the shape is (ndates,).
    """
    # Turn everything into arrays
    dates_arr: npt.NDArray[np.datetime64] = np.atleast_1d(dates).astype(np.datetime64)
    dates_arr_y = dates_arr.astype("datetime64[Y]")
    dates_arr_d = dates_arr.astype("datetime64[D]")
    dates_arr_s = dates_arr.astype("datetime64[s]")

    # dyear is DOY 1-366
    dyear: npt.NDArray[np.float64] = (dates_arr_d - dates_arr_y).astype(float) + 1.0
    dseconds: npt.NDArray[np.float64] = (dates_arr_s - dates_arr_d).astype(float)
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
        data = get_f107_ap(dates_arr, interpolate=interpolate_indices)
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
