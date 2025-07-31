# Changelog

All notable changes to this project will be documented in this file.

## [v0.11.0] 2025-07-30

- **MAINTENANCE** Default `-O2` optimization level for Linux/Mac and
  `-O0` for Windows. The Windows wheel tests fail with higher optimizations,
  but they can be set manually when building the project (see below for examples).
- **MAINTENANCE** Added aarch64 wheels.
- **PERFORMANCE** Supplying numpy datetime64 dates directly is much faster now and
  does not do an unnecessary extra copy of the data.

## [v0.10.0] 2024-11-19

- **ADDED** Top-level function exports to avoid submodule imports
  - `pymsis.calculate()` is the primrary entrypoint to running the MSIS
    model and calculating the atmosphere at the requested data points.
  - `pymsis.msis.run()` was not very descriptive and caused issues with IDL
    bridging into Python and wanting that name reserved. To avoid this, the
    function has been renamed `calculate` and is available as `pymsis.calculate()`
    now. The `pymsis.msis.run()` is still available as an alias for now, but
    may be removed in the future.
- **ADDED** Variable enumeration for easier indexing into output arrays.
  - This can be used as `pymsis.Variable.O2` for getting the `O2` species index.
    For example, `output_array[..., pymsis.Variable.O2]`.
- **ADDED** Python 3.13 and 3.13t support
- **ADDED** Multithreaded support.
  - The underlying MSIS libraries are not threadsafe due
    to the use of many global/save variables. There is a lock around the
    extension modules so that only one thread will be calling the routines
    at a time, so the Python library is safe to use in a multi-threaded context.
- **MAINTENANCE** Default `-O1` optimization level for all builds.
  - Previously, this
    was only done on Windows machines. Users can change this by updating
    environment variables before building with `FFLAGS=-Ofast pip install .`,
    but note that some machines produce invalid results when higher
    optimizations are used.
- **PERFORMANCE** Cache options state between subsequent runs.
  - Avoid calling initialization switches unless they have changed between runs
- **PERFORMANCE** Speed up numpy function calls.
  - Change some numpy broadcasting and comparisons to speed up the creation of
    input and output values.
- **MAINTENANCE** Add dynamic versioning to the project based on git tags and commits.
  - This removes the need to manually bump the version numbers and metadata before
    releasing the project which led to some errors previously.
- **DEPRECATED** Calling `msis00f.pytselec()` and `msis00f.pygtd7d` functions.
  - Use `msis00f.pyinitswitch` and `msis00f.pymsiscalc` instead.
  - This helps with standardization across the extension modules. These extension
    should rarely be used by external people and `pymsis.calculate()` is a better entry
    to using the package.

## [v0.9.0] - 2024-04-03

- **MAINTENANCE** Add MacOS arm64 wheels (Apple Silicon).
- **FIX** Obvious solar radio burst F10.7 data is automatically removed.
  - This applies to the default data and a warning is issued when running over
    these time periods.

## [v0.8.0] - 2023-10-03

- **MAINTENANCE** Python 3.10+ required.

## [v0.7.0] - 2023-01-29

### Maintenance

- **MAINTENANCE** CelesTrak is now used as the data provider for the Ap and F10.7 values.
  - This avoids data gaps and interpolation issues that were present in the source data.
- **MAINTENANCE** Cleanup type hints throughout the codebase.
- **MAINTENANCE** Updated the wrappers argument order to be the same throughout.
  - This helps when called with positional vs keyword arguments.

## [v0.6.0] - 2022-11-14

- **ADDED** Automatic download of F10.7 and ap data for users.
  - This means that F10.7 and ap are optional inputs to the `pymsis.calculate()`
    function during historical periods and the routines will automatically
    fetch the proper input data.

- **MAINTENANCE** We now use meson as the build system to compile the extension modules.

## [v0.5.0] - 2022-08-18

- **ADDED** MSIS2.1, a new version of MSIS.
  - This is the first version that contains NO.
  - This is the new default used in `pymsis.calculate()`.
- **MAINTENANCE** Added more wheels to the release and CI systems for testing.

## [v0.4.0] - 2022-02-26

- **ADDED** Created a DOI for the project: <https://doi.org/10.5281/zenodo.5348502>.
- **ADDED** Handle flattened input arrays directly (satellite flythroughs).

## [v0.3.0] - 2021-08-31

- **ADDED** First release with wheels for all platforms.
