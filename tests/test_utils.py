import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
import pytest

from pymsis import utils


def test_downloading(monkeypatch, tmp_path):
    tmp_file = tmp_path / "testfile.txt"
    monkeypatch.setattr(utils, "_F107_AP_PATH", tmp_file)
    # just be nice and make sure we are getting the monkeypatched local file
    assert utils._F107_AP_URL.startswith("file://")
    with pytest.warns(UserWarning, match="Downloading ap and F10.7"):
        utils.download_f107_ap()
    assert tmp_file.exists()
    with open(tmp_file, "rb") as f_downloaded, open(
        utils._F107_AP_PATH, "rb"
    ) as f_expected:
        assert f_downloaded.read() == f_expected.read()


def test_loading_data(monkeypatch, tmp_path):
    # Make sure we are starting off fresh with nothing loaded yet
    utils._DATA is None

    # Make sure a download warning is emitted if the file doesn't exist
    tmp_file = tmp_path / "testfile.txt"
    with monkeypatch.context() as m:
        m.setattr(utils, "_F107_AP_PATH", tmp_file)
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
    "dates,expected_f107,expected_f107a,expected_ap",
    [
        # First timestep of the file
        # No F10.7 the day before and average shouldn't be calculated
        # Ap should only have the daily value and the previous days
        (
            np.datetime64("2000-01-01T00:00"),
            [np.nan],
            [np.nan],
            [30, 56, np.nan, np.nan, np.nan, np.nan, np.nan],
        ),
        # Final timestep, the F107a can't be calculated
        (
            np.datetime64("2000-12-31T21:00"),
            [182.1],
            [np.nan],
            [2, 2, 0, 0, 3, 2.75, 4.125],
        ),
        # Middle of the data file, should be fully filled
        (
            np.datetime64("2000-07-01T12:00"),
            [159.6],
            [186.296296],
            [7, 4, 5, 9, 4, 5.25, 5.75],
        ),
        # Requesting two dates should return length two arrays
        (
            [np.datetime64("2000-07-01T12:00"), np.datetime64("2000-07-01T12:00")],
            [159.6, 159.6],
            [186.296296, 186.296296],
            [[7, 4, 5, 9, 4, 5.25, 5.75], [7, 4, 5, 9, 4, 5.25, 5.75]],
        ),
    ],
)
def test_get_f107_ap(dates, expected_f107, expected_f107a, expected_ap):
    f107, f107a, ap = utils.get_f107_ap(dates)
    assert_array_equal(f107, expected_f107)
    assert_allclose(f107a, expected_f107a)
    assert_array_equal(ap, expected_ap)


@pytest.mark.parametrize(
    "dates",
    [
        (np.datetime64("1999-12-31T23:00")),
        (np.datetime64("2001-01-01T00:00")),
        ([np.datetime64("2000-12-31T00:00"), np.datetime64("2001-01-01T00:00")]),
    ],
)
def test_get_f107_ap_out_of_range(dates):
    with pytest.raises(
        ValueError, match="The geomagnetic data is not available for these dates"
    ):
        utils.get_f107_ap(dates)
