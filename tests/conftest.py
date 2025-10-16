from pathlib import Path

import pytest

from pymsis import utils


@pytest.fixture(autouse=True)
def _path_setup(monkeypatch, tmp_path):
    # Monkeypatch the url and expected download location, so we aren't
    # dependent on an internet connection.
    monkeypatch.setattr(utils, "_F107_AP_PATH", tmp_path / "f107_ap_test_data.txt")

    # Update the remote URL to point to a local file system test path
    # by prepending file:// so that it can be opened by urlopen()
    test_file = Path(__file__).parent / "f107_ap_test_data.txt"
    test_url = test_file.absolute().as_uri()
    # Monkeypatch the url and expected download location, so we aren't
    # dependent on an internet connection.
    monkeypatch.setattr(utils, "_F107_AP_URL", test_url)
