# -*- coding: utf-8 -*-

"""
This is a tool for creating a new project based on a seed project. This tool
has ZERO dependencies, so you don't need to install any Python or set up any virtualenv.
It will automatically create a virtualenv and run the automation using the virtualenv's Python.

Requirements:

- Python 3.7+

How it works:

1. Each module in ``seeds`` directory is the template parameter settings for a seed project.
2. The ``cookiecutter_wrapper.py`` module imports the seed project template parameter settings,
    convert the seed project into a template project, then create a new project
    from the template project.
3. The ``more_project_like_this/cli.py`` and the ``cli.py`` script creates the
    CLI interface to create a new project from a seed project.
4. The ``automation.py`` module create a wrapper around the ``cookiecutter_wrapper.py``
    and the CLI, it automatically creates virtualenv and install dependencies,
    then run the CLI command.
"""

__version__ = "0.1.1"
