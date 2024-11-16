import concurrent.futures
from unittest.mock import patch

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from pymsis import msis, msis00f, msis20f, msis21f


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
def expected_output_with_options():
    return np.array(
        [
            2.427699e-10,
            2.849738e15,
            1.364307e14,
            3.836351e15,
            9.207778e12,
            1.490457e11,
            2.554763e12,
            3.459567e13,
            8.023306e-04,
            1.326593e12,
            9.277623e02,
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


@pytest.fixture
def input_auto_f107_ap():
    return (
        np.datetime64("2000-07-01T12:00"),
        0,
        0,
        200,
        159.6,
        186.3,
        [[7, 4, 5, 9, 4, 5.25, 5.75]],
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


def test_create_input_f107_date_mismatch(input_data):
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


@pytest.mark.parametrize("version", ["0", "2.0", "2.1"])
def test_create_input_lon_wrapping(input_data, expected_input, version):
    date, lon, lat, alt, f107, f107a, ap = input_data
    # Repeat 5 dates
    lons = np.array([-90] * 5)
    input_data = (date, lons, [lat] * 5, alt, f107, f107a, ap)
    shape, data = msis.create_input(*input_data)
    assert shape == (1, 5, 5, 1)
    assert data.shape == (5 * 5, 14)
    expected_input[2] = -90
    assert_array_equal(data, [expected_input] * 5 * 5)
    # Make sure that our input lons array wasn't transfomrmed inplace
    assert_array_equal(lons, [-90] * 5)

    # Test that -90 and 270 produce the same output
    assert_array_equal(
        msis.run(date, lons, [lat] * 5, alt, f107, f107a, ap, version=version),
        msis.run(date, lons + 360, [lat] * 5, alt, f107, f107a, ap, version=version),
    )


def test_run_options(input_data, expected_output):
    # Default options is all 1's, so make sure they are equivalent
    assert_allclose(
        np.squeeze(msis.run(*input_data, options=None)), expected_output, rtol=1e-5
    )
    assert_allclose(
        np.squeeze(msis.run(*input_data, options=[1] * 25)), expected_output, rtol=1e-5
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


def test_create_input_auto_f107(input_auto_f107_ap):
    date, lon, lat, alt, f107, f107a, ap = input_auto_f107_ap

    # What we put in is what we get out
    shape, data = msis.create_input(*input_auto_f107_ap)
    assert shape == (1,)
    assert data.shape == (1, 14)
    assert_allclose(data[0, :], [183, 43200, lon, lat, alt, f107, f107a, *ap[0]])

    # No f107
    _, test_data = msis.create_input(date, lon, lat, alt, f107as=f107a, aps=ap)
    assert_allclose(data, test_data)

    # No f107a
    _, test_data = msis.create_input(date, lon, lat, alt, f107s=f107, aps=ap)
    assert_allclose(data, test_data)

    # No ap
    _, test_data = msis.create_input(date, lon, lat, alt, f107s=f107, f107as=f107a)
    assert_allclose(data, test_data)

    # Nothing auto-fills
    _, test_data = msis.create_input(date, lon, lat, alt)
    assert_allclose(data, test_data)


def test_run_auto_f107(input_auto_f107_ap):
    # Dropping any of the f107/f107a/ap will go and get those
    # values automatically as needed
    date, lon, lat, alt, f107, f107a, ap = input_auto_f107_ap

    # fully specified run
    expected = msis.run(*input_auto_f107_ap)

    # auto
    assert_allclose(msis.run(date, lon, lat, alt), expected)

    # f107
    assert_allclose(msis.run(date, lon, lat, alt, f107s=f107), expected)

    # f107a
    assert_allclose(msis.run(date, lon, lat, alt, f107as=f107a), expected)

    # ap
    assert_allclose(msis.run(date, lon, lat, alt, aps=ap), expected)


@pytest.mark.parametrize(
    "inputs",
    [
        (np.datetime64("2000-01-01T00:00"), np.nan, 0, 100),
        (np.datetime64("2000-01-01T00:00"), 0, 0, 100),
        (np.datetime64("2000-01-01T00:00"), 0, 0, 100, np.nan),
    ],
)
def test_bad_run_inputs(inputs):
    # Inputs that have nan's in them at various places should all raise for the user
    with pytest.raises(ValueError, match="Input data has non-finite values"):
        msis.run(*inputs)


@pytest.mark.parametrize(
    ("version", "func"),
    [("0", msis00f.pygtd7d), ("2.0", msis20f.pymsiscalc), ("2.1", msis21f.pymsiscalc)],
)
def test_keyword_argument_call(input_data, version, func):
    # Make sure that the wrapper definition is correct for whether we
    # call it with or without keyword arguments
    date, lon, lat, alt, f107, f107a, ap = input_data
    dyear = (date.astype("datetime64[D]") - date.astype("datetime64[Y]")).astype(
        float
    ) + 1  # DOY 1-366
    dseconds = (date.astype("datetime64[s]") - date.astype("datetime64[D]")).astype(
        float
    )
    run_output = msis.run(
        dates=date,
        alts=alt,
        lats=lat,
        lons=lon,
        f107s=f107,
        f107as=f107a,
        aps=ap,
        version=version,
    )
    direct_output = func(
        day=np.array([dyear]),
        utsec=np.array([dseconds]),
        z=np.array([alt]),
        lat=np.array([lat]),
        lon=np.array([lon]),
        sflux=np.array([f107]),
        sfluxavg=np.array([f107a]),
        ap=np.array(ap),
    )
    if version < "2.1":
        # NO missing from versions before 2.1
        direct_output[:, -2] = np.nan
    assert_array_equal(run_output, direct_output)


def test_changing_options(input_data, expected_output, expected_output_with_options):
    # Calling the function again while just changing options should
    # also update the output data. There is global caching in MSIS,
    # so we need to make sure that we are actually changing the model
    # when the options change.
    assert_allclose(
        np.squeeze(msis.run(*input_data, options=[1] * 25)), expected_output, rtol=1e-5
    )
    assert_allclose(
        np.squeeze(msis.run(*input_data, options=[0] * 25)),
        expected_output_with_options,
        rtol=1e-5,
    )


def test_options_calls(input_data):
    # Check that we don't call the initialization function unless
    # our options have changed between calls.
    # Reset the cache
    for msis_lib in [msis00f, msis20f, msis21f]:
        msis_lib._last_used_options = None
    with patch("pymsis.msis21f.pyinitswitch") as mock_init:
        msis.run(*input_data, options=[0] * 25)
        mock_init.assert_called_once()
        msis.run(*input_data, options=[0] * 25)
        # Called again shouldn't call the initialization function
        mock_init.assert_called_once()

    # Our initialization function is different for MSIS00 and v2.0
    # This should still be called and not already set because
    # we've already run v2.1
    with patch("pymsis.msis20f.pyinitswitch") as mock_init:
        msis.run(*input_data, options=[0] * 25, version="2.0")
        mock_init.assert_called_once()
        msis.run(*input_data, options=[0] * 25, version="2.0")
        # Called again shouldn't call the initialization function
        mock_init.assert_called_once()
    with patch("pymsis.msis00f.pytselec") as mock_init:
        msis.run(*input_data, options=[0] * 25, version=0)
        mock_init.assert_called_once()
        msis.run(*input_data, options=[0] * 25, version=0)
        # Called again shouldn't call the initialization function
        mock_init.assert_called_once()


def test_multithreaded(
    input_data, expected_output, expected_output00, expected_output_with_options
):
    """
    Multithreaded run submission
    Make sure that we can run the function in a multithreaded environment
    and that the output is still correct and our global Fortran code hasn't
    been shared between threads incorrectly.
    NOTE: This will cause segfaults without the locks in place within the
          Python code.
    """
    # We need to make the list of items long enough to cause some computation
    # within the Fortran code during each run() call.
    date, lon, lat, alt, f107, f107a, ap = input_data
    n = 2000
    input_data = (
        [date] * n,
        [lon] * n,
        [lat] * n,
        [alt] * n,
        [f107] * n,
        [f107a] * n,
        ap * n,
    )
    # Create a tuple of items (version, options, expected_output)
    # 3 items cycled over 100 times
    list_of_inputs = [
        (0, None, np.tile(expected_output00, (n, 1))),
        (2.1, None, np.tile(expected_output, (n, 1))),
        (2.1, [0] * 25, np.tile(expected_output_with_options, (n, 1))),
    ] * 100

    def run_function(input_items):
        version, options, expected = input_items
        return np.squeeze(
            msis.run(*input_data, version=version, options=options)
        ), expected

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the load operations and mark each future with its URL
        results = [executor.submit(run_function, x) for x in list_of_inputs]

    for future in results:
        result, expected_result = future.result()
        assert_allclose(result, expected_result, rtol=1e-5)
