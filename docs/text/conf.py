"""Sphinx configuration for the plopm documentation."""

from __future__ import annotations

import os
import sys
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = DOCS_DIR.parents[1]
SRC_DIR = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

project = "plopm"
copyright = "2024-2026, NORCE Research AS"
author = "David Landa-Marbán"

try:
    release = package_version("plopm")
except PackageNotFoundError:
    release = os.environ.get("PLOPM_DOCS_VERSION", "development")
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"
add_module_names = False

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}

root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

smartquotes = False

toc_object_entries = True
toc_object_entries_show_parents = "hide"

html_theme = "pydata_sphinx_theme"
html_title = "plopm documentation"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_context = {
    "github_user": "cssr-tools",
    "github_repo": "plopm",
    "github_version": "main",
    "doc_path": "docs/text",
}

html_logo = "figs/plopm-logo.svg"

html_theme_options = {
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_persistent": ["search-button"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_align": "content",
    "header_links_before_dropdown": 8,
    "show_toc_level": 2,
    "navigation_depth": 4,
    "collapse_navigation": True,
    "show_nav_level": 1,
    "back_to_top_button": True,
    "secondary_sidebar_items": ["page-toc", "edit-this-page", "sourcelink"],
    "logo": {
        "alt_text": "plopm documentation - Home",
    },
    "icon_links": [
        {
            "name": "Report an issue",
            "url": "https://github.com/cssr-tools/plopm/issues/new/choose",
            "icon": "fa-solid fa-bug",
            "type": "fontawesome",
        },
        {
            "name": "GitHub repository",
            "url": "https://github.com/cssr-tools/plopm",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
}

pygments_style = "sphinx"
pygments_dark_style = "monokai"

copybutton_prompt_text = r">>> |\.\.\. |\$ |# "
copybutton_prompt_is_regexp = True

html_show_sourcelink = True
html_show_sphinx = False
html_last_updated_fmt = "%Y-%m-%d"
