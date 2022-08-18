import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
import pytest

from pymsis import msis


@pytest.fixture
def input_data():
    date = np.datetime64("2010-01-01T12:00")
    lon = 0
    lat = 0
    alt = 200
    f107 = 150
    f107a = 150
    ap = [[3] * 7]
    return (date, lon, lat, alt, f107, f107a, ap)


@pytest.fixture
def expected_input():
    return [1.0, 86400 / 2, 0, 0, 200, 150, 150] + [3] * 7


@pytest.fixture
def expected_output():
    return np.array(
        [
            2.466441e-10,
            2.929253e15,
            1.250981e14,
            3.845766e15,
            8.506817e12,
            1.300092e11,
            2.662435e12,
            5.717013e13,
            3.302753e-04,
            2.204773e12,
            9.846238e02,
        ],
        dtype=np.float32,
    )


@pytest.fixture
def expected_output00():
    return np.array(
        [
            2.790941e-10,
            3.354463e15,
            1.242698e14,
            4.331106e15,
            8.082919e12,
            1.126601e11,
            2.710179e12,
            5.634838e13,
            1.665595e-03,
            np.nan,
            9.838066e02,
        ],
        dtype=np.float32,
    )


def test_create_options():
    options = [
        "f107",
        "time_independent",
        "symmetrical_annual",
        "symmetrical_semiannual",
        "asymmetrical_annual",
        "asymmetrical_semiannual",
        "diurnal",
        "semidiurnal",
        "geomagnetic_activity",
        "all_ut_effects",
        "longitudinal",
        "mixed_ut_long",
        "mixed_ap_ut_long",
        "terdiurnal",
    ]

    # Default is all 1's
    assert [1] * 25 == msis.create_options()

    # Check each individual keyword argument
    for i, opt in enumerate(options):
        expected = [1] * 25
        expected[i] = 0
        assert expected == msis.create_options(**{opt: 0})

    # Check multiple keyword arguments
    expected = [0] * 14 + [1] * 11
    assert expected == msis.create_options(**{opt: 0 for opt in options})


def test_create_input_single_point(input_data, expected_input):
    shape, data = msis.create_input(*input_data)
    assert shape == (1,)
    assert data.shape == (1, 14)
    assert_array_equal(data[0, :], expected_input)


def test_create_input_datetime(input_data, expected_input):
    # Test with datetime, not just np.datetime64s
    # .item() gets the datetime object from the np.datetime64 object
    input_data = (input_data[0].item(),) + input_data[1:]
    shape, data = msis.create_input(*input_data)
    assert shape == (1,)
    assert data.shape == (1, 14)
    assert_array_equal(data[0, :], expected_input)


def test_create_input_f107__date_mismatch(input_data):
    # Make sure we raise when f107 and dates are different shapes
    # Repeat 5 dates, but not f107
    input_data = ([input_data[0]] * 5,) + input_data[1:]
    with pytest.raises(ValueError, match="The length of dates"):
        msis.create_input(*input_data)


def test_create_input_multi_date(input_data, expected_input):
    date, lon, lat, alt, f107, f107a, ap = input_data
    # Repeat 5 dates
    input_data = ([date] * 5, lon, lat, alt, [f107] * 5, [f107a] * 5, ap * 5)
    shape, data = msis.create_input(*input_data)
    assert shape == (5, 1, 1, 1)
    assert data.shape == (5, 14)
    assert_array_equal(data, [expected_input] * 5)


def test_create_input_multi_lon(input_data, expected_input):
    date, lon, lat, alt, f107, f107a, ap = input_data
    # Repeat 5 dates
    input_data = (date, [lon] * 5, lat, alt, f107, f107a, ap)
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 5, 1, 1)
    assert data.shape == (5, 14)
    assert_array_equal(data, [expected_input] * 5)


def test_create_input_multi_lat(input_data, expected_input):
    date, lon, lat, alt, f107, f107a, ap = input_data
    # Repeat 5 dates
    input_data = (date, lon, [lat] * 5, alt, f107, f107a, ap)
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 1, 5, 1)
    assert data.shape == (5, 14)
    assert_array_equal(data, [expected_input] * 5)


def test_create_input_multi_alt(input_data, expected_input):
    date, lon, lat, alt, f107, f107a, ap = input_data
    # Repeat 5 dates
    input_data = (date, lon, lat, [alt] * 5, f107, f107a, ap)
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 1, 1, 5)
    assert data.shape == (5, 14)
    assert_array_equal(data, [expected_input] * 5)


def test_create_input_multi_lon_lat(input_data, expected_input):
    date, lon, lat, alt, f107, f107a, ap = input_data
    # Repeat 5 dates
    input_data = (date, [lon] * 5, [lat] * 5, alt, f107, f107a, ap)
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 5, 5, 1)
    assert data.shape == (5 * 5, 14)
    assert_array_equal(data, [expected_input] * 5 * 5)


def test_run_options(input_data):
    # Default options is all 1's, so make sure they are equivalent
    assert_array_equal(
        msis.run(*input_data, options=None), msis.run(*input_data, options=[1] * 25)
    )

    with pytest.raises(ValueError, match="options needs to be a list"):
        msis.run(*input_data, options=[1] * 22)


def test_run_single_point(input_data, expected_output):
    output = msis.run(*input_data)
    assert output.shape == (1, 11)
    assert_allclose(np.squeeze(output), expected_output, rtol=1e-5)


def test_run_gridded_multi_point(input_data, expected_output):
    date, lon, lat, alt, f107, f107a, ap = input_data
    # 5 x 5 surface
    input_data = (date, [lon] * 5, [lat] * 5, alt, f107, f107a, ap)
    output = msis.run(*input_data)
    assert output.shape == (1, 5, 5, 1, 11)
    expected = np.tile(expected_output, (5, 5, 1))
    assert_allclose(np.squeeze(output), expected, rtol=1e-5)


def test_run_multi_point(input_data, expected_output):
    # test multi-point run, like a satellite fly-through
    # and make sure we don't grid the input data
    # 5 input points
    date, lon, lat, alt, f107, f107a, ap = input_data
    input_data = (
        [date] * 5,
        [lon] * 5,
        [lat] * 5,
        [alt] * 5,
        [f107] * 5,
        [f107a] * 5,
        ap * 5,
    )
    output = msis.run(*input_data)
    assert output.shape == (5, 11)
    expected = np.tile(expected_output, (5, 1))
    assert_allclose(np.squeeze(output), expected, rtol=1e-5)


def test_run_wrapped_lon(input_data, expected_output):
    date, _, lat, alt, f107, f107a, ap = input_data

    input_data = (date, -180, lat, alt, f107, f107a, ap)
    output1 = msis.run(*input_data)
    input_data = (date, 180, lat, alt, f107, f107a, ap)
    output2 = msis.run(*input_data)
    assert_allclose(output1, output2, rtol=1e-5)

    input_data = (date, 0, lat, alt, f107, f107a, ap)
    output1 = msis.run(*input_data)
    input_data = (date, 360, lat, alt, f107, f107a, ap)
    output2 = msis.run(*input_data)
    assert_allclose(output1, output2, rtol=1e-5)


def test_run_poles(input_data):
    # Test that moving in longitude around a pole
    # returns the same values
    # North pole
    date, _, _, alt, f107, f107a, ap = input_data
    input_data = (date, 0, 90, alt, f107, f107a, ap)
    output1 = msis.run(*input_data)
    input_data = (date, 20, 90, alt, f107, f107a, ap)
    output2 = msis.run(*input_data)
    assert_allclose(output1, output2, rtol=1e-5)

    # South pole
    input_data = (date, 0, -90, alt, f107, f107a, ap)
    output1 = msis.run(*input_data)
    input_data = (date, 20, -90, alt, f107, f107a, ap)
    output2 = msis.run(*input_data)
    assert_allclose(output1, output2, rtol=1e-5)


def test_run_versions(input_data):
    # Make sure we accept these version numbers and don't throw an error
    for ver in [0, 2, "00", "2"]:
        msis.run(*input_data, version=ver)
    # Test for something outside of that list for an error to be thrown
    with pytest.raises(ValueError, match="The MSIS version selected"):
        msis.run(*input_data, version=1)


def test_run_version00(input_data, expected_output00):
    output = msis.run(*input_data, version=0)
    assert output.shape == (1, 11)
    assert_allclose(np.squeeze(output), expected_output00, rtol=1e-5)


def test_run_multi_point00(input_data, expected_output00):
    date, lon, lat, alt, f107, f107a, ap = input_data
    # 5 x 5 surface
    input_data = (date, [lon] * 5, [lat] * 5, alt, f107, f107a, ap)
    output = msis.run(*input_data, version=0)
    assert output.shape == (1, 5, 5, 1, 11)
    expected = np.tile(expected_output00, (5, 5, 1))
    assert_allclose(np.squeeze(output), expected, rtol=1e-5)


def test_run_version00_low_altitude(input_data):
    # There is no O, H, N below 72.5 km, should be NaN
    date, lon, lat, _, f107, f107a, ap = input_data
    input_data = (date, lon, lat, 71, f107, f107a, ap)
    output = msis.run(*input_data, version=0)
    assert np.all(np.isnan(np.squeeze(output)[[3, 5, 7]]))
