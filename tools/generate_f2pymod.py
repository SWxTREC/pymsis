"""Generate the f2py wrappers."""

import argparse
import os
import subprocess
import sys


def main():
    """Run the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str, help="Path to the input file")
    parser.add_argument("-o", "--outdir", type=str, help="Path to the output directory")
    args = parser.parse_args()

    if not args.infile.endswith(".pyf"):
        raise ValueError(f"Input file has unknown extension: {args.infile}")

    outdir_abs = os.path.join(os.getcwd(), args.outdir)

    # Now invoke f2py to generate the C API module file
    if args.infile.endswith((".pyf.src", ".pyf")):
        p = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "numpy.f2py",
                args.infile,
                "--build-dir",
                outdir_abs,
                "--freethreading-compatible",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd(),
        )
        out, err = p.communicate()
        if not (p.returncode == 0):
            raise RuntimeError(
                f"Writing {args.outfile} with f2py failed!\n" f"{out}\n" r"{err}"
            )


if __name__ == "__main__":
    main()
