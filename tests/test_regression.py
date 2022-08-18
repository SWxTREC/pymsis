from pathlib import Path
import numpy as np
from numpy.testing import assert_allclose

from pymsis import msis


def run_input_line(line, version):
    items = line.split()
    expected = np.array(items[9:], dtype=np.float32)

    # Needs to be "-3:" due to strip() taking off leading spaces
    doy = int(items[0][-3:]) - 1  # Python wants DOY to start with 0
    sec, alt, lat, lon, _, f107a, f107, ap = (float(x) for x in items[1:9])
    ap = [[ap] * 7]
    year = int(items[0][:-3])
    # Two digit year
    if year > 60:
        year += 1900
    else:
        year += 2000
    date = (
        np.datetime64(str(year))
        + np.timedelta64(doy, "D")
        + np.timedelta64(int(sec), "s")
    )

    test_inp = (date, lon, lat, alt, f107, f107a, ap)
    test_output = np.squeeze(msis.run(*test_inp, version=version))

    # Rearrange the run's output to match the expected
    # ordering of elements
    if version == "2.0":
        x = np.array(
            [
                test_output[4],
                test_output[3],
                test_output[1],
                test_output[2],
                test_output[6],
                test_output[0],
                test_output[5],
                test_output[7],
                test_output[8],
                test_output[10],
            ]
        )
    elif version == "2.1":
        x = np.array(
            [
                test_output[4],
                test_output[3],
                test_output[1],
                test_output[2],
                test_output[6],
                test_output[0],
                test_output[5],
                test_output[7],
                test_output[8],
                test_output[9],
                test_output[10],
            ]
        )
    else:
        raise ValueError("Version number incorrect")

    # Different units in the test file (cgs)
    x[np.isclose(x, 9.9e-38, atol=1e-38)] = np.nan
    x[:-1] *= 1e-6
    x[5] *= 1e3
    x[np.isnan(x)] = 9.999e-38
    # The output print statements are messy.
    # They technically give 4 decimal places, but only truly 3 decimal places
    # in scientific notation. Example: 0.8888e+23 -> 8.888e+24
    # We will require relative comparisons of 2e-3 to account for the
    # last digit errors.
    assert_allclose(x, expected, rtol=2e-3)


def test_included_msis20_f90_file():
    # Regressing to the included file
    TEST_DIR = Path(__file__).parent
    with open(TEST_DIR / "msis2.0_test_ref_dp.txt") as f:
        f.readline()  # Header
        for line in f:
            run_input_line(line, version="2.0")


def test_included_msis_21_f90_file():
    # Regressing to the included file
    TEST_DIR = Path(__file__).parent
    with open(TEST_DIR / "msis2.1_test_ref_dp.txt") as f:
        f.readline()  # Header
        for line in f:
            run_input_line(line, version="2.1")
