"""Only for CI downloading/testing."""

import tarfile
import urllib.request
from pathlib import Path


MSIS21_FILE = (
    "https://gist.github.com/greglucas/"
    "6a545a4ccbfdb93290a96ad13a0b6f81/"
    "raw/3f82de72d2ea5df7b1cfe492a6b2efee55349f95/"
    "nrlmsis2.1.tar.gz"
)

with urllib.request.urlopen(MSIS21_FILE) as stream:
    tf = tarfile.open(fileobj=stream, mode="r|gz")
    tf.extractall(path=Path("src/msis2.1/"))

# MSIS2 Tar file
MSIS20_FILE = (
    "https://gist.github.com/greglucas/"
    "6a545a4ccbfdb93290a96ad13a0b6f81/"
    "raw/8a853f3e1c2b324f1c4ea9e0fa1e6d073258a456/"
    "NRLMSIS2.0.tar.gz"
)

with urllib.request.urlopen(MSIS20_FILE) as stream:
    tf = tarfile.open(fileobj=stream, mode="r|gz")
    tf.extractall(path=Path("src/msis2.0/"))

# MSIS-00 fortran file
MSIS00_FILE = (
    "https://gist.githubusercontent.com/greglucas/"
    "6a545a4ccbfdb93290a96ad13a0b6f81/"
    "raw/2c1f5d899d7b42392a6b19a041d2cc213589a5f1/"
    "NRLMSISE-00.FOR"
)
with urllib.request.urlopen(MSIS00_FILE) as response:
    with open(Path("src/msis00/NRLMSISE-00.FOR"), "wb") as f:
        f.write(response.read())
