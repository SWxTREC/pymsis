"""Utilities for obtaining input datasets."""

import urllib.request
import warnings
from io import BytesIO
from pathlib import Path
from typing import Optional

import numpy as np
import numpy.typing as npt

import pymsis


_DATA_FNAME: str = "SW-All.csv"
_F107_AP_URL: str = f"https://celestrak.org/SpaceData/{_DATA_FNAME}"
_F107_AP_PATH: Path = Path(pymsis.__file__).parent / _DATA_FNAME
_DATA: Optional[dict[str, npt.NDArray]] = None


def download_f107_ap() -> None:
    """
    Download the latest ap and F10.7 values.

    The file is downloaded into the installed package location, keeping
    the same filename as the data source: `SW-All.csv`.
    This routine can be called to update the data as well if you would like to
    use newer data since the last time you downloaded the file.

    Notes
    -----
    The data provider we are using is CelesTrak, which gets data from other
    sources and interpolates or predicts missing values to make data easier to
    work with. A warning is emitted when the interpolation or prediction
    occurs, but it is up to the user to verify the Ap and F10.7 data that is used
    is correct for their application.
    Use of this geomagnetic data should cite the references [1]_ [2]_.

    References
    ----------
    .. [1] CelesTrak. https://celestrak.org/SpaceData/
    .. [2] Matzka, J., Stolle, C., Yamazaki, Y., Bronkalla, O. and Morschhauser, A.,
       2021. The geomagnetic Kp index and derived indices of geomagnetic activity.
       Space Weather, https://doi.org/10.1029/2020SW002641
    """
    warnings.warn(f"Downloading ap and F10.7 data from {_F107_AP_URL}")
    req = urllib.request.urlopen(_F107_AP_URL)
    with _F107_AP_PATH.open("wb") as f:
        f.write(req.read())


def _load_f107_ap_data() -> dict[str, npt.NDArray]:
    """Load data from disk, if it isn't present go out and download it first."""
    if not _F107_AP_PATH.exists():
        download_f107_ap()

    dtype = {
        "names": (
            "date",
            "ap1",
            "ap2",
            "ap3",
            "ap4",
            "ap5",
            "ap6",
            "ap7",
            "ap8",
            "Ap",
            "f107",
            "f107-type",
            "f107a",
        ),
        "formats": (
            "datetime64[D]",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "f8",
            "S3",
            "f8",
        ),
    }
    usecols = (0, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 26, 27)

    # Use a buffer to read in and load so we can quickly get rid of
    # the extra "PRD" lines at the end of the file (unknown length
    # so we can't just go back in line lengths)
    with _F107_AP_PATH.open() as fin:
        with BytesIO() as fout:
            for line in fin:
                if "PRM" in line:
                    # We don't want the monthly predicted values
                    continue
                fout.write(line.encode("utf-8"))
            fout.seek(0)
            arr = np.loadtxt(
                fout, delimiter=",", dtype=dtype, usecols=usecols, skiprows=1
            )  # type: ignore

    # transform each day's 8 3-hourly ap values into a single column
    ap = np.empty(len(arr) * 8, dtype=float)
    daily_ap = arr["Ap"].astype(float)
    dates = np.repeat(arr["date"], 8).astype("datetime64[m]")
    for i in range(8):
        ap[i::8] = arr[f"ap{i+1}"]
        dates[i::8] += i * np.timedelta64(3, "h")

    # data file has missing values as negatives
    ap[ap < 0] = np.nan
    daily_ap[daily_ap < 0] = np.nan
    # There are also some non-physical f10.7 values
    # F10.7 > 400 is unrealistic indicating a solar radio burst
    solar_radio_burst = 400
    bad_f107 = (arr["f107"] <= 0) | (arr["f107"] > solar_radio_burst)
    # Set the data to the 81-day average as a temporary fix
    arr["f107"][bad_f107] = arr["f107a"][bad_f107]
    # flag it as interpolated or predicted values so we warn the user
    arr["f107-type"][bad_f107] = b"INT"

    ap_data = np.ones((len(ap), 7)) * np.nan
    # daily Ap
    # repeat each value for each 3-hourly interval
    ap_data[:, 0] = np.repeat(arr["Ap"], 8)
    # current 3-hour ap index value
    ap_data[:, 1] = ap
    # 3-hours before current time
    ap_data[1:, 2] = ap[:-1]
    # 6-hours before current time
    ap_data[2:, 3] = ap[:-2]
    # 9-hours before current time
    ap_data[3:, 4] = ap[:-3]
    # average of 12-33 hours prior to current time
    # calculate the rolling mean with a convolution window length of 8
    # we want to offset by 4 because we are starting at the 12th hour,
    # then adjust for the valid mode with an edge-length of (8-1)
    rolling_mean = np.convolve(ap, np.ones(8) / 8, mode="valid")
    ap_data[4 + 8 - 1 :, 5] = rolling_mean[:-4]
    # average of 36-57 hours prior to current time
    # Use the same window length as before, just shifting the fill values
    ap_data[4 + 16 - 1 :, 6] = rolling_mean[: -(4 + 8)]

    # F107 Data is needed from the previous day, F107a centered on the current day
    f107_data = np.ones(len(arr), dtype=float) * np.nan
    f107a_data = np.ones(len(arr), dtype=float) * np.nan
    f107_data[1:] = arr["f107"][:-1]
    f107a_data = arr["f107a"]
    # So that we can warn the user that this F107 data was interpolated or predicted
    interpolated = b"INT"
    predicted = b"PRD"
    warn_data = (arr["f107-type"] == interpolated) | (arr["f107-type"] == predicted)
    # Because we use the F107 from the day before, we need to shift the warning
    # to the following day when we would actually use the value
    warn_data[1:] = warn_data[:-1]

    # Set the global module-level data variable
    data = {
        "dates": dates,
        "ap": ap_data,
        "f107": f107_data,
        "f107a": f107a_data,
        "warn_data": warn_data,
    }
    globals()["_DATA"] = data
    return data


def get_f107_ap(dates: npt.ArrayLike) -> tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    """
    Retrieve the F10.7 and ap data needed to run msis for the given times.

    The MSIS model uses historical F10.7 and ap values for the calculations,
    and these are also derived quantities.

    Parameters
    ----------
    dates : datetime-like or sequence of datetimes
        times of interest to get the proper ap and F10.7 values for

    Returns
    -------
    tuple (f107 [n], f107a [n], ap [n x 7])
        Three arrays containing the f107, f107a, and ap values
        corresponding to the input times of length n.

        f107 : np.ndarray
            Daily F10.7 of the previous day for the given date(s)
        f107a : np.ndarray
            F10.7 running 81-day average centered on the given date(s)
        ap : np.ndarray
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
    """
    dates = np.asarray(dates, dtype=np.datetime64)
    data = _DATA or _load_f107_ap_data()

    data_start = data["dates"][0]
    data_end = data["dates"][-1]
    date_offsets = dates - data_start
    # daily index values
    daily_indices = date_offsets.astype("timedelta64[D]").astype(int)
    # 3-hourly index values
    ap_indices = date_offsets.astype("timedelta64[h]").astype(int) // 3

    if np.any((ap_indices < 0) | (ap_indices >= len(data["ap"]))):
        # We are requesting data outside of the valid range
        raise ValueError(
            "The geomagnetic data is not available for these dates. "
            f"Dates should be between {data_start} and "
            f"{data_end}."
        )

    f107 = np.take(data["f107"], daily_indices)
    f107a = np.take(data["f107a"], daily_indices)
    ap = np.take(data["ap"], ap_indices, axis=0)
    warn_or_not = np.take(data["warn_data"], daily_indices)
    # TODO: Do we want to warn if any values within 81 days of a point are used?
    #      i.e. if any of the f107a values were interpolated or predicted
    if np.any(warn_or_not):
        warnings.warn(
            "There is data that was either interpolated or predicted "
            "(not observed), use at your own risk."
        )
    return f107, f107a, ap
