from pathlib import Path
from typing import Any
import urllib.request
import warnings

import numpy as np
import pymsis


_DATA_FNAME: str = "Kp_ap_Ap_SN_F107_since_1932.txt"
_AP_F107_URL: str = f"https://kp.gfz-potsdam.de/app/files/{_DATA_FNAME}"
_AP_F107_PATH: Path = Path(pymsis.__file__).parent / _DATA_FNAME
# total days is from 1932-01-01 00:00 according to the header of the file
_AP_START_DATE: np.datetime64 = np.datetime64("1932-01-01 00:00")
_DATA: dict = None


def download_ap_f107():
    """
    Download the latest ap and F10.7 values

    The download path is to the installed package location keeping
    the same filename as the data source: `Kp_ap_Ap_SN_F107_since_1932.txt`. [1]_

    References
    ----------
    .. [1] Matzka, J., Stolle, C., Yamazaki, Y., Bronkalla, O. and Morschhauser, A., 2021.
       The geomagnetic Kp index and derived indices of geomagnetic activity.
       Space Weather, https://doi.org/10.1029/2020SW002641
    """
    warnings.warn(f"Downloading ap and F10.7 data from {_AP_F107_URL}")
    req = urllib.request.urlopen(_AP_F107_URL)
    with open(_AP_F107_PATH, "wb") as f:
        f.write(req.read())


def _load_ap_f107_data():
    """Load data from disk, if it isn't present go out and download it first"""
    if not _AP_F107_PATH.exists():
        download_ap_f107()

    dtype = {
        "names": (
            "total days",
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
        ),
        "formats": (
            "timedelta64[D]",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "i4",
            "f4",
        ),
    }
    usecols = (3, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25)
    arr = np.loadtxt(_AP_F107_PATH, dtype=dtype, usecols=usecols)

    # transform each day's 8 3-hourly ap values into a single column
    ap = np.empty(len(arr) * 8, dtype=float)
    daily_ap = arr["Ap"].astype(float)
    dates = _AP_START_DATE + np.arange(len(ap)) * np.timedelta64(3, "h")
    for i in range(8):
        ap[i::8] = arr[f"ap{i+1}"]

    # data file has missing values as negatives
    ap[ap < 0] = np.nan
    daily_ap[daily_ap < 0] = np.nan
    # There are also some non-physical f10.7 values
    arr["f107"][arr["f107"] <= 0] = np.nan

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

    # F107 Data is needed from the previous day
    f107_data = np.ones(len(arr)) * np.nan
    f107a_data = np.ones(len(arr)) * np.nan
    f107_data[1:] = arr["f107"][:-1]
    # average of 81-days, centered on the current day
    rolling_mean = np.convolve(arr["f107"], np.ones(81) / 81, mode="valid")
    f107a_data[40:-40] = rolling_mean

    # Set the global module-level data variable
    data = {"dates": dates, "ap": ap_data, "f107": f107_data, "f107a": f107a_data}
    globals()["_DATA"] = data
    return data


def get_ap_f107(times):
    """
    Retrieve the ap and F10.7 data needed to run msis for the given times.

    The MSIS model uses historical ap and F10.7 values for the calculations,
    and these are also derived quantities.

    Parameters
    ----------
    times : datetime-like or sequence of datetimes
        times of interest to get the proper ap and F10.7 values for

    Returns
    -------
    tuple (ap [n x 7], f107 [n], f107a [n])
        Three arrays containing the ap, f107, and f107a values
        corresponding to the input times of length n.
    """
    times = np.asarray(times, dtype=np.datetime64)
    data = _DATA or _load_ap_f107_data()

    # 3-hourly index values
    ap_indices = (times - _AP_START_DATE).astype("timedelta64[h]").astype(int) // 3
    # daily index values
    daily_indices = (times - _AP_START_DATE).astype("timedelta64[D]").astype(int)

    ap = np.take(data["ap"], ap_indices, axis=0)
    f107 = np.take(data["f107"], daily_indices)
    f107a = np.take(data["f107a"], daily_indices)
    return ap, f107, f107a
