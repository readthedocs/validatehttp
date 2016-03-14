# -*- coding: utf-8 -*-
#
import sys
import os

project = u'validatehttp'
copyright = u'2016, Anthony Johnson'
author = u'Anthony Johnson'
version = u'1.0'
release = u'1.0'
language = None

extensions = []
html_theme = 'alabaster'
templates_path = ['_templates']
html_static_path = ['_static']

source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = False
htmlhelp_basename = 'validatehttpdoc'

latex_elements = {}
latex_documents = [
    (master_doc, 'validatehttp.tex', u'validatehttp Documentation',
     u'Anthony Johnson', 'manual'),
]
man_pages = [
    (master_doc, 'validatehttp', u'validatehttp Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'validatehttp', u'validatehttp Documentation',
     author, 'validatehttp', 'One line description of project.',
     'Miscellaneous'),
]
