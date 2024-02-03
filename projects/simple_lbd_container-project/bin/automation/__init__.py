# -*- coding: utf-8 -*-

"""
At very beginning, we need create virtual environment and install some dependencies.
However, setting up virtual environment and installing dependencies requires
additional dependencies such as ``virtualenv``, ``poetry``, which may not be
available in the global Python you use.

This module can be run in any Python, and it automatically installs those
bootstrap dependencies, and set up the virtualenv environment and project
dependencies for you.

Requirements:

- Python >= 3.7
- See requirements-jumpstart.txt
"""

from ._version import __version__

__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__license__ = "MIT"
