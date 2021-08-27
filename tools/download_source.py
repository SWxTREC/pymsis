import glob
import os
import tarfile
import urllib.request
import warnings

SOURCE_DIR = "https://map.nrl.navy.mil/map/pub/nrl/NRLMSIS/"
MSIS2_FILE = SOURCE_DIR + "NRLMSIS2.0/NRLMSIS2.0.tar.gz"
MSIS00_FILE = SOURCE_DIR + "NRLMSISE-00/NRLMSISE-00.FOR"


def get_source():
    """Download and install the Fortran source code."""
    # Start with MSIS2
    if not os.path.exists(os.path.join('src', 'msis2', 'msis_init.F90')):
        # No source code yet, so go download and extract it
        try:
            warnings.warn("Downloading the MSIS2 source code from "
                          f"{MSIS2_FILE}")
            with urllib.request.urlopen(MSIS2_FILE) as stream:
                tf = tarfile.open(fileobj=stream, mode="r|gz")
                tf.extractall(path=os.path.join('src', 'msis2', ''))
        except Exception as e:
            print("Downloading the source code from the original repository "
                  "failed. You can manually download and extract the source "
                  "code following instructions in the README.")
            raise e

    # Rename the parameter file to what the Fortran is expecting
    if not os.path.exists('pymsis/msis2.0.parm'):
        # Notice that the original is "20", not "2.0"
        os.rename(os.path.join('src', 'msis2', 'msis20.parm'),
                  os.path.join('pymsis', 'msis2.0.parm'))

    # Now go through and clean the source files
    clean_utf8(glob.glob(os.path.join('src', 'msis2', '*.F90')))

    # Now go to MSIS-00
    if not os.path.exists(os.path.join('src', 'msis00', 'NRLMSISE-00.FOR')):
        # No source code yet, so go download and extract it
        try:
            warnings.warn("Downloading the MSIS-00 source code from "
                          f"{MSIS00_FILE}")

            with urllib.request.urlopen(MSIS00_FILE) as response:
                with open(os.path.join('src', 'msis00', 'NRLMSISE-00.FOR'),
                          'wb') as f:
                    f.write(response.read())
        except Exception as e:
            print("Downloading the source code from the original repository "
                  "failed. You can manually download and extract the source "
                  "code following instructions in the README.")
            raise e

    # Fix up the file outside of the download incase it is an offline install
    fix_msis00(os.path.join('src', 'msis00', 'NRLMSISE-00.FOR'))


# Clean up the source files
def clean_utf8(fnames):
    """Remove bad characters.

    fnames: list
        filenames to be cleaned
    """
    for fname in fnames:
        with open(fname, 'rb+') as f:
            # Ignore bad decode errors
            data = f.read().decode('utf-8', 'ignore')
            # write the good encoded bytes out to the same file
            f.seek(0)
            f.write(data.encode('utf-8'))
            f.truncate()


def fix_msis00(fname):
    """Fix bad lines in msis00

    The gfortran compiler thinks there is a character/int mismatch,
    so fix these bad lines.

    fname: string
        filename of the file to be fixed
    """
    # Example of the bad line
    # NRLMSISE-00.FOR:1671:10:

    #       DATA NAME/'MSIS','E-00'/
    #          1
    # Error: Incompatible types in DATA statement at (1);
    # attempted conversion of CHARACTER(1) to INTEGER(4)

    bad1 = ("DATA ISDATE/'01-F','EB-0','2   '/,ISTIME/'15:4','9:27'/",
            "DATA ISDATE/4H13-A,4HPR-0,4H0   /,ISTIME/4H17:4,4H6:08/")
    bad2 = ("DATA NAME/'MSIS','E-00'/", "DATA NAME/4HMSIS,4HE-00/")
    with open(fname, 'r+') as f:
        data = f.read()
        data = data.replace(bad1[0], bad1[1]).replace(bad2[0], bad2[1])
        f.seek(0)
        f.write(data)
        f.truncate()


if __name__ == "__main__":
    get_source()
