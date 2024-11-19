.. _api:

API reference
=============
.. currentmodule:: pymsis

This page gives an overview of the routines within the pymsis package.
To calculate atmospheric constituents at grid points, use the :func:`~.calculate` function.
This is typically the only function you will need to use. You can access the output variables
using the :class:`~.Variable` enumeration for easier indexing into the output data array.
For example, as ``output_array[..., Variable.MASS_DENSITY]``.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    calculate
    Variable

msis module
-----------

For more control and help creating properly formatted inputs, one can
use the :mod:`pymsis.msis` module. This module provides functions to
create input data, create the options list, and run the model.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    msis.create_input
    msis.create_options
    msis.calculate

utils module
------------

The MSIS model requires solar forcing data (F10.7 and ap) to calculate the state of the atmosphere.
When running over past time periods, this data is automatically downloaded and used if not specified by the user.
For more control over the F10.7 and Ap values the model is using, one can input the desired values
into the :func:`~.calculate` call ``calculate(..., f107s=..., f107as=..., aps=...)``.
To get the values used automatically by the model, the :mod:`pymsis.utils` module has several
helper routines to download new files (will retrieve a file with data up to the present) and
get the proper F10.7 and ap values to use for a specific date and time.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    utils.download_f107_ap
    utils.get_f107_ap
