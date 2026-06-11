# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------

project = "ece4-exp"
copyright = "2026, Vladimir Lapin (BSC)"
author = "Vladimir Lapin"
release = "1.0.2"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "style_external_links": True,
}

# -- RST substitutions -------------------------------------------------------

rst_prolog = """
.. |ece4exp| replace:: ece4-exp
.. |ecearth4| replace:: EC-Earth4
"""
