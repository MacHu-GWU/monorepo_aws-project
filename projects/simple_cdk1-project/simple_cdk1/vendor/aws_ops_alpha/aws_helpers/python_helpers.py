# -*- coding: utf-8 -*-

"""
This module implements the automation to manage Python project.
"""

import typing as T
import subprocess
from textwrap import dedent


if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops


def bump_version(
    pyproject_ops: "pyops.PyProjectOps",
    major: bool = False,
    minor: bool = False,
    patch: bool = False,
):  # pragma: no cover
    if sum([patch, minor, major]) != 1:
        raise ValueError(
            "Only one and exact one of 'is_patch', 'is_minor', 'is_major' can be True"
        )

    # get the current version
    major, minor, micro = pyproject_ops.package_version.split(".")
    major, minor, micro = int(major), int(minor), int(micro)

    # update version
    if major:
        action = "major"
        major += 1
        minor, micro = 0, 0
        # print(f"{major}.{minor}.{mirco}")
    elif minor:
        action = "minor"
        minor += 1
        micro = 0
    elif patch:
        action = "patch"
        micro += 1
    else:  # pragma: no cover
        raise NotImplementedError
    new_version = f"{major}.{minor}.{micro}"

    # update _version.py file
    version_py_content = dedent(
        """
    __version__ = "{}"

    # keep this ``if __name__ == "__main__"``, don't delete!
    # this is used by automation script to detect the project version
    if __name__ == "__main__":  # pragma: no cover
        print(__version__)
    """
    ).strip()
    version_py_content = version_py_content.format(new_version)
    pyproject_ops.path_version_py.write_text(version_py_content)

    # update pyproject.toml file
    with pyproject_ops.dir_project_root.temp_cwd():
        args = [
            pyproject_ops.path_bin_poetry,
            "version",
            action,
        ]
        subprocess.run(args, check=True)
