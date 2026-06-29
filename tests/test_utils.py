import importlib

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from pymsis import utils


def test_downloading(monkeypatch, tmp_path):
    tmp_file = tmp_path / "testfile.txt"
    # download_f107_ap() always writes to the default location, so patch both
    monkeypatch.setattr(utils, "_F107_AP_PATH", tmp_file)
    monkeypatch.setattr(utils, "_F107_AP_DEFAULT_PATH", tmp_file)
    # just be nice and make sure we are getting the monkeypatched local file
    assert utils._F107_AP_URL.startswith("file://")
    with pytest.warns(UserWarning, match="Downloading ap and F10.7"):
        utils.download_f107_ap()
    assert tmp_file.exists()
    with (
        open(tmp_file, "rb") as f_downloaded,
        open(utils._F107_AP_PATH, "rb") as f_expected,
    ):
        assert f_downloaded.read() == f_expected.read()


def test_loading_data(monkeypatch, tmp_path):
    # Make sure we are starting off fresh with nothing loaded yet
    utils._DATA = None

    # Make sure a download warning is emitted if the file doesn't exist
    tmp_file = tmp_path / "testfile.txt"
    with monkeypatch.context() as m:
        # Point both at the (missing) default location so the auto-download
        # branch is exercised rather than the custom-path branch.
        m.setattr(utils, "_F107_AP_PATH", tmp_file)
        m.setattr(utils, "_F107_AP_DEFAULT_PATH", tmp_file)
        assert not tmp_file.exists()
        with pytest.warns(UserWarning, match="Downloading ap and F10.7"):
            utils._load_f107_ap_data()
    assert utils._DATA is not None

    # If the file is already present locally we don't want a download warning
    utils._DATA = None
    utils._load_f107_ap_data()
    assert utils._DATA is not None

    # Now make some assertions on the loaded data
    data = utils._DATA
    assert data["dates"][0] == np.datetime64("2000-01-01T00:00")
    assert data["dates"][-1] == np.datetime64("2000-12-31T21:00")
    expected_data_length = (
        np.datetime64("2001-01-01T00:00") - np.datetime64("2000-01-01T00:00")
    ).astype("timedelta64[h]").astype(int) // 3
    assert len(data["dates"]) == expected_data_length
    assert len(data["ap"]) == expected_data_length
    # F10.7 is daily and therefore should be 1/8 the size
    expected_data_length //= 8
    assert len(data["f107"]) == expected_data_length
    assert len(data["f107a"]) == expected_data_length


@pytest.mark.parametrize(
    ("dates", "expected_f107", "expected_f107a", "expected_ap"),
    [
        # First timestep of the file
        # No F10.7 the day before
        # Ap should only have the daily value and the previous days
        (
            np.datetime64("2000-01-01T00:00"),
            [np.nan],
            [166.2],
            [[30, 56, np.nan, np.nan, np.nan, np.nan, np.nan]],
        ),
        # Middle of the data file, should be fully filled
        (
            np.datetime64("2000-07-01T12:00"),
            [159.6],
            [186.3],
            [[7, 4, 5, 9, 4, 5.25, 5.75]],
        ),
        # Requesting two dates should return length two arrays
        (
            [np.datetime64("2000-07-01T12:00"), np.datetime64("2000-07-01T12:00")],
            [159.6, 159.6],
            [186.3, 186.3],
            [[7, 4, 5, 9, 4, 5.25, 5.75], [7, 4, 5, 9, 4, 5.25, 5.75]],
        ),
        # Bad F10.7 value artificially added to 2000-12-29 test file
        # should be replaced with F10.7a value on that same day
        (
            np.datetime64("2000-12-30T12:00"),
            [173.7],
            [173.5],
            [[3, 4, 4, 3, 3, 6.375, 5.375]],
        ),
    ],
)
@pytest.mark.filterwarnings("ignore:There is data that was either interpolated")
def test_get_f107_ap(dates, expected_f107, expected_f107a, expected_ap):
    f107, f107a, ap = utils.get_f107_ap(dates)
    assert_array_equal(f107, expected_f107)
    assert_allclose(f107a, expected_f107a)
    assert_array_equal(ap, expected_ap)


@pytest.mark.parametrize(
    "dates",
    [
        # edge cases
        (np.datetime64("1999-12-31T23:00")),
        (np.datetime64("2001-01-01T00:00")),
        # Array of dates should raise if one of them is outside the bounds
        ([np.datetime64("2000-12-31T00:00"), np.datetime64("2001-01-01T00:00")]),
        # Extreme cases
        (np.datetime64("1900-01-01T00:00")),
        (np.datetime64("2100-01-01T00:00")),
    ],
)
def test_get_f107_ap_out_of_range(dates):
    with pytest.raises(
        ValueError, match="The geomagnetic data is not available for these dates"
    ):
        utils.get_f107_ap(dates)


@pytest.mark.parametrize(
    "dates",
    [
        (np.datetime64("2000-12-30T00:00")),  # Bad data inserted
        (np.datetime64("2000-12-31T00:00")),  # Interpolated data
        ([np.datetime64("2000-12-01T00:00"), np.datetime64("2000-12-31T00:00")]),
    ],
)
def test_get_f107_ap_interpolated_warns(dates):
    with pytest.warns(
        UserWarning, match="There is data that was either interpolated or"
    ):
        utils.get_f107_ap(dates)


@pytest.mark.parametrize(
    ("date", "expected_f107", "expected_ap_col1"),
    [
        # At exact boundary (00:00), interpolated should match step values
        ([np.datetime64("2000-07-01T00:00")], 159.6, 9.0),
        # At 3-hour boundary: ap should match, f107 interpolates within day
        ([np.datetime64("2000-07-01T03:00")], 160.1125, 4.0),
        # Mid-way through 3-hour window (01:30): both ap and f107 interpolate
        ([np.datetime64("2000-07-01T01:30")], 159.85625, 6.5),
    ],
)
def test_get_f107_ap_interpolate(date, expected_f107, expected_ap_col1):
    """Test linear interpolation of F10.7 and ap values."""
    f107, _, ap = utils.get_f107_ap(date, interpolate=True)
    assert_allclose(f107[0], expected_f107)
    assert_allclose(ap[0, 1], expected_ap_col1)


@pytest.mark.parametrize(
    "date",
    [
        np.datetime64("2000-01-01T00:00"),
        np.datetime64("2000-07-01T00:00"),
        np.datetime64("2000-07-02T00:00"),
    ],
)
def test_get_f107_ap_interpolate_exact_match(date):
    """Test that interpolation at exact data points returns the same as no interp."""
    f107_nointerp, f107a_nointerp, ap_nointerp = utils.get_f107_ap(
        date, interpolate=False
    )
    f107_interp, f107a_interp, ap_interp = utils.get_f107_ap(date, interpolate=True)
    assert_allclose(f107_nointerp, f107_interp)
    assert_allclose(f107a_nointerp, f107a_interp)
    assert_array_equal(ap_nointerp, ap_interp)


def test_use_space_weather_file(monkeypatch, tmp_path):
    custom_file = tmp_path / "custom_sw.csv"
    custom_file.write_text("placeholder")
    # Pretend some data was already cached so we can verify it gets reset
    monkeypatch.setattr(utils, "_DATA", {"dummy": np.array([1])})

    utils.use_space_weather_file(custom_file)
    # Check if the path has been updated
    assert utils._F107_AP_PATH == custom_file
    # Check if the data has been reset.
    assert utils._DATA is None

    # Setting a path that doesn't exist should raise
    missing = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        utils.use_space_weather_file(missing)

    # downloading should raise a warning that the file is ignored.
    # Redirect the download to a throwaway path so we don't overwrite shared test data.
    monkeypatch.setattr(utils, "_F107_AP_DEFAULT_PATH", tmp_path / "downloaded.csv")
    with pytest.warns(UserWarning, match="A custom space weather file has been set"):
        utils.download_f107_ap()


def test_space_weather_env_variable(monkeypatch, tmp_path):
    # check if setting space weather path via env variable works
    custom_file = tmp_path / "custom_sw.csv"
    custom_file.write_text("placeholder")
    monkeypatch.setenv("PYMSIS_SPACE_WEATHER_PATH", str(custom_file))
    importlib.reload(utils)

    assert utils._F107_AP_PATH == custom_file

    # Loading the data must validate that the file exists.
    missing = tmp_path / "does_not_exist.csv"
    monkeypatch.setenv("PYMSIS_SPACE_WEATHER_PATH", str(missing))
    importlib.reload(utils)
    with pytest.raises(FileNotFoundError, match="Custom space weather file"):
        utils._load_f107_ap_data()
