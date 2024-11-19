.. _api:

API reference
=============
.. currentmodule:: pymsis

This page gives an overview of the routines within the pymsis package.
To run the code, use the :mod:`pymsis.msis` module.

.. autosummary::
    :toctree: generated/

    msis.run
    msis.create_options
    msis.create_input

The output of the model is stored in basic numpy arrays with the final
dimension being the variable/species. To get the output in a more human-readable
format, use the :class:`~.Variable` enumeration that provides
easier indexing into the output arrays.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    msis.Variable

To get input data for historical events, use the :mod:`pymsis.utils` module.

.. autosummary::
    :toctree: generated/

    utils.download_f107_ap
    utils.get_f107_ap