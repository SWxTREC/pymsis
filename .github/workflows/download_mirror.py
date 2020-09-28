"""This is only for CI downloading/testing."""
import tarfile
import urllib.request

SOURCE_FILE = ("https://gist.github.com/greglucas/"
               "6a545a4ccbfdb93290a96ad13a0b6f81/"
               "raw/8a853f3e1c2b324f1c4ea9e0fa1e6d073258a456/"
               "NRLMSIS2.0.tar.gz")

with urllib.request.urlopen(SOURCE_FILE) as stream:
    tf = tarfile.open(fileobj=stream, mode="r|gz")
    tf.extractall(path='msis2/')
