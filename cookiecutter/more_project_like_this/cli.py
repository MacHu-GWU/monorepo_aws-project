# -*- coding: utf-8 -*-

"""
.. note::

    This module has to be run in virtualenv Python
"""

from .cookiecutter_wrapper import new_project


class Command:
    def new(self, seed: str):
        new_project(seed=seed)
