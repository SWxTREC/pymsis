import numpy as np
import pytest

from pymsis2 import msis2


def test_data():
    date = np.datetime64('2010-01-01T12:00')
    lon = 0
    lat = 0
    alt = 200
    f107 = 150
    f107a = 150
    ap = [[3]*7]
    return (date, lon, lat, alt, f107, f107a, ap)


def test_create_options():
    options = ['f107', 'time_independent', 'symmetrical_annual',
               'symmetrical_semiannual', 'asymmetrical_annual',
               'asymmetrical_semiannual', 'diurnal', 'semidiurnal',
               'geomagnetic_activity', 'all_ut_effects', 'longitudinal',
               'mixed_ut_long', 'mixed_ap_ut_long', 'terdiurnal']

    # Default is all 1's
    assert [1]*25 == msis2.create_options()

    # Check each individual keyword argument
    for i, opt in enumerate(options):
        expected = [1]*25
        expected[i] = 0
        assert expected == msis2.create_options(**{opt: 0})

    # Check multiple keyword arguments
    expected = [0]*14 + [1]*11
    assert expected == msis2.create_options(**{opt: 0 for opt in options})


def test_create_input_single_point():
    input_data = test_data()
    shape, data = msis2.create_input(*input_data)
    assert shape == (1, 1, 1, 1)
    assert data.shape == (1, 14)
    expected = [1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7
    np.testing.assert_array_equal(data[0, :], expected)


def test_create_input_datetime():
    # Test with datetime, not just np.datetime64s
    input_data = test_data()
    # .item() gets the datetime object from the np.datetime64 object
    input_data = (input_data[0].item(),) + input_data[1:]
    shape, data = msis2.create_input(*input_data)
    assert shape == (1, 1, 1, 1)
    assert data.shape == (1, 14)
    expected = [1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7
    np.testing.assert_array_equal(data[0, :], expected)


def test_create_input_f107__date_mismatch():
    # Make sure we raise when f107 and dates are different shapes
    input_data = test_data()
    # Repeat 5 dates
    input_data = ([input_data[0]]*5, ) + input_data[1:]
    with pytest.raises(ValueError, match='The length of dates'):
        msis2.create_input(*input_data)


def test_create_input_multi_date():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = ([date]*5, lon, lat, alt, [f107]*5, [f107a]*5, ap*5)
    shape, data = msis2.create_input(*input_data)
    assert shape == (5, 1, 1, 1)
    assert data.shape == (5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5
    np.testing.assert_array_equal(data, expected)


def test_create_input_multi_lon():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = (date, [lon]*5, lat, alt, f107, f107a, ap)
    shape, data = msis2.create_input(*input_data)
    assert shape == (1, 5, 1, 1)
    assert data.shape == (5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5
    np.testing.assert_array_equal(data, expected)


def test_create_input_multi_lat():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = (date, lon, [lat]*5, alt, f107, f107a, ap)
    shape, data = msis2.create_input(*input_data)
    assert shape == (1, 1, 5, 1)
    assert data.shape == (5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5
    np.testing.assert_array_equal(data, expected)


def test_create_input_multi_alt():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = (date, lon, lat, [alt]*5, f107, f107a, ap)
    shape, data = msis2.create_input(*input_data)
    assert shape == (1, 1, 1, 5)
    assert data.shape == (5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5
    np.testing.assert_array_equal(data, expected)


def test_create_input_multi_lon_lat():
    date, lon, lat, alt, f107, f107a, ap = test_data()
    # Repeat 5 dates
    input_data = (date, [lon]*5, [lat]*5, alt, f107, f107a, ap)
    shape, data = msis2.create_input(*input_data)
    assert shape == (1, 5, 5, 1)
    assert data.shape == (5*5, 14)
    expected = [[1.5, 86400/2, 0, 0, 200, 150, 150] + [3]*7]*5*5
    np.testing.assert_array_equal(data, expected)
