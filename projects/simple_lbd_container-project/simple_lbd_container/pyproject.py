# -*- coding: utf-8 -*-

"""
`pyproject_ops <https://github.com/MacHu-GWU/pyproject_ops-project>`_ library
provides a set of utilities to automate common devops tasks for Python projects.
If you follow the code structure defined in ``pyproject_ops``, you can do these
things::

    # create virtual environment for this project
    >>> pyproject_ops.create_virtualenv()
    # install core dependencies
    >>> pyproject_ops.pip_install()
    # install additional dependencies for dev, doc, test
    >>> pyproject_ops.pip_install_all()
    # run code coverage test
    >>> pyproject_ops.run_cov_test()
"""

import sys

from pyproject_ops.api import PyProjectOps

from .paths import dir_project_root, PACKAGE_NAME
from .runtime import runtime

# we still need this variable for import, but will not use this in lambda runtime
if runtime.is_aws_lambda:  # pragma: no cover
    pyproject_ops = None
else:
    pyproject_ops = PyProjectOps(
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
        package_name=PACKAGE_NAME,
        dir_project_root=dir_project_root,
    )
