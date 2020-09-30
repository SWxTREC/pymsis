import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
import pytest

from pymsis import msis


def test_data():
    date = np.datetime64('2010-01-01T12:00')
    lon = 0
    lat = 0
    alt = 200
    f107 = 150
    f107a = 150
    ap = [[3]*7]
    return (date, lon, lat, alt, f107, f107a, ap)


def test_output():
    return np.array([2.465493e-10, 2.927530e+15, 1.251696e+14, 3.845063e+15,
                     8.492528e+12, 1.300680e+11, 2.661727e+12, 5.718397e+13,
                     3.302753e-04, np.nan, 9.845342e+02],
                    dtype=np.float32)


def test_create_options():
    options = ['f107', 'time_independent', 'symmetrical_annual',
               'symmetrical_semiannual', 'asymmetrical_annual',
               'asymmetrical_semiannual', 'diurnal', 'semidiurnal',
               'geomagnetic_activity', 'all_ut_effects', 'longitudinal',
               'mixed_ut_long', 'mixed_ap_ut_long', 'terdiurnal']

    # Default is all 1's
    assert [1]*25 == msis.create_options()

    # Check each individual keyword argument
    for i, opt in enumerate(options):
        expected = [1]*25
        expected[i] = 0
        assert expected == msis.create_options(**{opt: 0})

    # Check multiple keyword arguments
    expected = [0]*14 + [1]*11
    assert expected == msis.create_options(**{opt: 0 for opt in options})


def test_create_input_single_point():
    input_data = test_data()
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 1, 1, 1)
    assert data.shape == (1, 14)
    expected = [1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7
    assert_array_equal(data[0, :], expected)


def test_create_input_datetime():
    # Test with datetime, not just np.datetime64s
    input_data = test_data()
    # .item() gets the datetime object from the np.datetime64 object
    input_data = (input_data[0].item(),) + input_data[1:]
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 1, 1, 1)
    assert data.shape == (1, 14)
    expected = [1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7
    assert_array_equal(data[0, :], expected)


def test_create_input_f107__date_mismatch():
    # Make sure we raise when f107 and dates are different shapes
    input_data = test_data()
    # Repeat 5 dates
    input_data = ([input_data[0]]*5, ) + input_data[1:]
    with pytest.raises(ValueError, match='The length of dates'):
        msis.create_input(*input_data)


def test_create_input_multi_date():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = ([date]*5, lon, lat, alt, [f107]*5, [f107a]*5, ap*5)
    shape, data = msis.create_input(*input_data)
    assert shape == (5, 1, 1, 1)
    assert data.shape == (5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5
    assert_array_equal(data, expected)


def test_create_input_multi_lon():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = (date, [lon]*5, lat, alt, f107, f107a, ap)
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 5, 1, 1)
    assert data.shape == (5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5
    assert_array_equal(data, expected)


def test_create_input_multi_lat():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = (date, lon, [lat]*5, alt, f107, f107a, ap)
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 1, 5, 1)
    assert data.shape == (5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5
    assert_array_equal(data, expected)


def test_create_input_multi_alt():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = (date, lon, lat, [alt]*5, f107, f107a, ap)
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 1, 1, 5)
    assert data.shape == (5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5
    assert_array_equal(data, expected)


def test_create_input_multi_lon_lat():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = (date, [lon]*5, [lat]*5, alt, f107, f107a, ap)
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 5, 5, 1)
    assert data.shape == (5*5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5*5
    assert_array_equal(data, expected)


def test_run_options():
    # Default options is all 1's, so make sure they are equivalent
    assert_array_equal(msis.run(*test_data(), options=None),
                       msis.run(*test_data(), options=[1]*25))

    with pytest.raises(ValueError, match='options needs to be a list'):
        msis.run(*test_data(), options=[1]*22)


def test_run_single_point():
    output = msis.run(*test_data())
    assert output.shape == (1, 1, 1, 1, 11)
    assert_allclose(np.squeeze(output), test_output(), rtol=1e-5)


def test_run_multi_point():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # 5 x 5 surface
    input_data = (date, [lon]*5, [lat]*5, alt, f107, f107a, ap)
    output = msis.run(*input_data)
    assert output.shape == (1, 5, 5, 1, 11)
    expected = np.tile(test_output(), (5, 5, 1))
    assert_allclose(np.squeeze(output), expected, rtol=1e-5)


def test_run_wrapped_lon():
    date, _, lat, alt, f107, f107a, ap = test_data()

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


def test_run_poles():
    # Test that moving in longitude around a pole
    # returns the same values
    # North pole
    date, _, _, alt, f107, f107a, ap = test_data()
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
