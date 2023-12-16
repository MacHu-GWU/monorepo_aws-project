# -*- coding: utf-8 -*-

"""
This library automates CI/CD processes by running terminal commands,
building artifacts, and deploying applications. It follows a "shell scripting"
style to implement most of the logic, effectively separating the
automation processes from the main application source code. This design made
this library reusable for other projects.

Some automation requires config data from the "Real" application
source code. However, we don't import any code from the "Real" application
code base. Instead, we define arguments in the Python function that allow user
to integrate the automation library with the "Real" application code base freely.

Requirements:

- Python >= 3.8
- See requirements-automation.txt
"""

from ._version import __version__

__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__license__ = "MIT"
