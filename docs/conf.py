# -*- coding: utf-8 -*-
#

project = "validatehttp"
copyright = "2016, Anthony Johnson"
author = "Anthony Johnson"
version = "1.0"
release = "1.0"
language = None

extensions = []
html_theme = "alabaster"
templates_path = ["_templates"]
html_static_path = ["_static"]

source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build"]
pygments_style = "sphinx"
todo_include_todos = False
htmlhelp_basename = "validatehttpdoc"

latex_elements = {}
latex_documents = [
    (master_doc, "validatehttp.tex", "validatehttp Documentation", "Anthony Johnson", "manual"),
]
man_pages = [(master_doc, "validatehttp", "validatehttp Documentation", [author], 1)]
texinfo_documents = [
    (
        master_doc,
        "validatehttp",
        "validatehttp Documentation",
        author,
        "validatehttp",
        "One line description of project.",
        "Miscellaneous",
    ),
]
