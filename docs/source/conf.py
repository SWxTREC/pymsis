"""
Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Path setup --------------------------------------------------------------

import importlib.metadata
import sys

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use resolve() to make it absolute, like shown here.
#
from pathlib import Path

from sphinx_gallery.sorting import ExampleTitleSortKey, ExplicitOrder


sys.path.insert(0, Path("../../pymsis").resolve())

# -- Project information -----------------------------------------------------

project = "pymsis"
copyright = "2020, Regents of the University of Colorado"
author = "Greg Lucas"

# The full version, including alpha/beta/rc tags
version = importlib.metadata.version("pymsis")
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "matplotlib.sphinxext.plot_directive",
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.githubpages",  # Helpful for publishing to gh-pages
    "sphinx.ext.napoleon",
    "sphinx_gallery.gen_gallery",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

html_logo = "_static/pymsis-logo.png"

html_theme_options = {
    "github_url": "https://github.com/SWxTREC/pymsis",
    "navbar_start": ["navbar-logo", "version"],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Autosummary
autosummary_generate = True
autodoc_typehints = "none"

# Define subsection order for examples gallery
subsection_order = ExplicitOrder(
    [
        "../../examples/general_examples",
        "../../examples/options_overview",
        "../../examples/individual_options",
    ]
)

# Sphinx gallery
sphinx_gallery_conf = {
    "examples_dirs": "../../examples",
    "gallery_dirs": "examples",
    "matplotlib_animations": True,
    "within_subsection_order": ExampleTitleSortKey,
    "subsection_order": subsection_order,
}
