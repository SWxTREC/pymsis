"""This is only for CI downloading/testing."""
import os
import tarfile
import urllib.request

# MSIS2 Tar file
SOURCE_FILE = ("https://gist.github.com/greglucas/"
               "6a545a4ccbfdb93290a96ad13a0b6f81/"
               "raw/8a853f3e1c2b324f1c4ea9e0fa1e6d073258a456/"
               "NRLMSIS2.0.tar.gz")

with urllib.request.urlopen(SOURCE_FILE) as stream:
    tf = tarfile.open(fileobj=stream, mode="r|gz")
    tf.extractall(path=os.path.join('src', 'msis2', ''))

# MSIS-00 fortran file
MSIS00_FILE = ("https://gist.githubusercontent.com/greglucas/"
               "6a545a4ccbfdb93290a96ad13a0b6f81/"
               "raw/2c1f5d899d7b42392a6b19a041d2cc213589a5f1/"
               "NRLMSISE-00.FOR")
with urllib.request.urlopen(MSIS00_FILE) as response:
    with open(os.path.join('src', 'msis00', 'NRLMSISE-00.FOR'), 'wb') as f:
        f.write(response.read())
