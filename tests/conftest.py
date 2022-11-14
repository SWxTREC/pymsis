from pathlib import Path

import pytest

from pymsis import utils


@pytest.fixture(autouse=True)
def local_path(monkeypatch):
    # Update the data location to our test data
    test_file = Path(__file__).parent / "f107_ap_test_data.txt"
    # Monkeypatch the url and expected download location, so we aren't
    # dependent on an internet connection.
    monkeypatch.setattr(utils, "_F107_AP_PATH", test_file)
    yield test_file


@pytest.fixture(autouse=True)
def remote_path(monkeypatch, local_path):
    # Update the remote URL to point to a local file system test path
    # by prepending file:// so that it can be opened by urlopen()
    test_url = local_path.absolute().as_uri()
    # Monkeypatch the url and expected download location, so we aren't
    # dependent on an internet connection.
    monkeypatch.setattr(utils, "_F107_AP_URL", test_url)
    yield test_url
