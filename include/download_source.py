import fileinput
import glob
import os
import tarfile
import urllib.request

SOURCE_FILE = ("https://map.nrl.navy.mil/map/pub/nrl/NRLMSIS/"
               "NRLMSIS2.0/NRLMSIS2.0.tar.gz")


def get_source():
    """Download and install the Fortran source code."""
    if not os.path.exists('msis2'):
        os.makedirs('msis2')

    if not os.path.exists('msis2/msis_init.F90'):
        # No source code yet, so go download and extract it
        try:
            stream = urllib.request.urlopen(SOURCE_FILE)
            tf = tarfile.open(fileobj=stream, mode="r|gz")
            tf.extractall(path='msis2/')
        except Exception as e:
            print("Downloading the source code from the original repository "
                  "failed. You can manually download and extract the source "
                  "code following instructions in the README.")
            raise e

    # Rename the parameter file to what the Fortran is expecting
    if not os.path.exists('msis2/msis2.0.parm'):
        os.rename('msis2/msis20.parm', 'msis2/msis2.0.parm')

    # Now go through and clean the source files
    clean_utf8(glob.glob('msis2/*.F90'))


# Clean up the source files
def clean_utf8(fnames):
    """Remove bad characters.

    fnames: list
        filenames to be cleaned
    """
    with fileinput.input(files=fnames, mode='rb',
                         inplace=True, backup='.bak') as f:
        for line in f:
            # Decode the line ignoring bad characters
            print(line.decode('utf-8', 'ignore'), end='')


if __name__ == "__main__":
    get_source()
