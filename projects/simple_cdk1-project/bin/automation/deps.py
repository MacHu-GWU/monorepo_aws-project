# -*- coding: utf-8 -*-

"""
This module automates dependencies management.

We use `Python poetry <https://python-poetry.org/>`_ to ensure determinative dependencies.
"""

from aws_ops_alpha.api import runtime
from .pyproject import pyproject_ops
from .logger import logger


quiet = True if runtime.is_ci else False


def pip_install():
    pyproject_ops.pip_install(quiet=quiet, verbose=True)


def pip_install_dev():
    pyproject_ops.pip_install_dev(quiet=quiet, verbose=True)


def pip_install_test():
    pyproject_ops.pip_install_test(quiet=quiet, verbose=True)


def pip_install_doc():
    pyproject_ops.pip_install_doc(quiet=quiet, verbose=True)


def pip_install_automation():
    pyproject_ops.pip_install_automation(quiet=quiet, verbose=True)


def pip_install_all():
    pyproject_ops.pip_install_all(quiet=quiet, verbose=True)


def pip_install_all_in_ci():
    if pyproject_ops.path_venv_bin_pytest.exists() is False:
        pyproject_ops.pip_install_all(quiet=quiet, verbose=True)
    else:
        logger.info("dependencies are already installed, do nothing")
