# -*- coding: utf-8 -*-

"""
Automation script for virtualenv_bootstrap.

This script has ZERO DEPENDENCY.

Usage 1, use this script as a module:

    >>> from virtualenv_bootstrap import Project
    >>> project = Project.new()
    >>> project.bootstrap()
    🐍 Create virtualenv at /path/to/.venv
        ✅ Virtualenv already exists
    💾 Install necessary dependencies in virtualenv
        ✅ Done

Usage 2, use this script as a command line tool:

    $ python virtualenv_bootstrap --dir_project_root /path/to/project/root --python_version 3.9 --path_requirements_txt /path/to/requirements.txt
"""

import typing as T
import sys
import re
import subprocess
import dataclasses
import shutil
from pathlib import Path

__version__ = "0.0.1"

p1 = re.compile("^\d+\.\d+$")
p2 = re.compile("^python\d+\.\d+$")


def get_python_interpreter_full_path(path_python: Path) -> Path:
    args = [
        f"{path_python}",
        "-c",
        "import sys; print(sys.executable)",
    ]
    response = subprocess.run(args, capture_output=True, check=True)
    return Path(response.stdout.decode("utf-8").strip())


def get_pip_full_path(path_python: Path) -> Path:
    if path_python.name == "python":
        return path_python.parent / "pip"
    else:
        return path_python.parent / ("pip" + path_python.name[-3:])


@dataclasses.dataclass
class Project:
    """
    The metadata about the Python project that include a virtualenv and dependencies.
    """

    # fmt: off
    path_python: Path = dataclasses.field()
    path_pip: Path = dataclasses.field()
    path_virtualenv: Path = dataclasses.field()
    dir_venv: Path = dataclasses.field()
    path_requirements_txt: Path = dataclasses.field()
    # fmt: on

    @classmethod
    def new(
        cls,
        path_python: T.Optional[T.Union[str, Path]] = None,
        dir_venv: T.Optional[T.Union[str, Path]] = None,
        path_requirements_txt: T.Optional[T.Union[str, Path]] = None,
    ):
        """
        Factory method.

        :param path_python: the base Python interpreter for virtualenv, valid
            values are: ``3.9``, ``python3.9``, ``/path/to/pythonX.Y``
        :param dir_venv: the directory of virtualenv, there will be a ``bin``
            directory in ``dir_venv``. If not specified, it will be the
            ``.venv`` in the current working directory.
        :param path_requirements_txt: the path to ``requirements.txt``, which
            contains the dependencies to be installed in the virtualenv.
            If not specified, it will be the ``requirements.txt`` in the
            current working directory.
        """
        dir_cwd = Path.cwd()
        if path_python is None:
            _path_python = Path(sys.executable)
        # example: 3.9
        elif isinstance(path_python, str) and re.match(p1, path_python):
            python_version = path_python
            _path_python = Path(shutil.which(f"python{python_version}"))
            _path_python = get_python_interpreter_full_path(_path_python)
            # example: python3.9
        elif isinstance(path_python, str) and re.match(p2, path_python):
            python_version = path_python[6:]
            _path_python = Path(shutil.which(path_python))
            _path_python = get_python_interpreter_full_path(_path_python)
        # example: /path/to/python/interpreter
        else:
            _path_python = Path(path_python)
            if _path_python.exists():
                pass
            elif dir_cwd.joinpath(_path_python).exists():
                _path_python = str(dir_cwd.joinpath(_path_python))
            else:
                raise FileNotFoundError(
                    f"Python interpreter not found at {path_python}"
                )
            _path_python = get_python_interpreter_full_path(_path_python)

        _path_pip = get_pip_full_path(_path_python)
        _path_virtualenv = _path_python.parent / "virtualenv"

        if dir_venv is None:
            dir_venv = dir_cwd / ".venv"
        else:
            dir_venv = Path(dir_venv).absolute()

        if path_requirements_txt is None:
            path_requirements_txt = dir_cwd / "requirements.txt"
            if path_requirements_txt.exists() is False:
                raise FileNotFoundError(
                    f"requirements.txt not found at {path_requirements_txt}"
                )
        else:
            path_requirements_txt = Path(path_requirements_txt).absolute()

        return cls(
            path_python=_path_python,
            path_pip=_path_pip,
            path_virtualenv=_path_virtualenv,
            dir_venv=dir_venv,
            path_requirements_txt=path_requirements_txt,
        )

    @property
    def path_venv_bin(self) -> Path:
        return self.dir_venv / "bin"

    @property
    def path_venv_bin_python(self) -> Path:
        return self.path_venv_bin / "python"

    @property
    def path_venv_bin_pip(self) -> Path:
        return self.path_venv_bin / "pip"

    def install_virtualenv(self):
        """
        The base Python may not have virtualenv installed. Install it if necessary.
        """
        if self.path_virtualenv.exists() is False:
            args = [f"{self.path_pip}", "install", "virtualenv"]
            subprocess.run(args, check=True)

    def create_virtualenv(
        self,
        recreate: bool = False,
    ):
        """
        Create a virtualenv.

        :param recreate: If True, delete the existing virtualenv before creating a new one.
            If False, do nothing if the virtualenv already exists.
        """
        print(f"🐍 Create virtualenv at {self.dir_venv}")
        self.install_virtualenv()

        if self.dir_venv.exists():
            if recreate:
                shutil.rmtree(self.dir_venv, ignore_errors=True)
            else:
                print(f"  ✅ Virtualenv already exists")
                return
        args = [
            f"{self.path_virtualenv}",
            "-p",
            f"{self.path_python}",
            f"{self.dir_venv}",
        ]
        subprocess.run(args, check=True)
        print("  ✅ Done")

    def install_dependencies_in_virtualenv(
        self,
        quite: bool = True,
    ):
        """
        Install dependencies in the virtualenv.
        """
        print(f"💾 Install necessary dependencies in virtualenv")
        args = [
            f"{self.path_venv_bin_pip}",
            "install",
        ]
        if quite:
            args.append("-q")
        args.extend(
            [
                "--disable-pip-version-check",
                "-r",
                f"{self.path_requirements_txt}",
            ]
        )
        subprocess.run(args, check=True)
        print("  ✅ Done")

    def bootstrap(
        self,
        recreate_venv: bool = False,
    ):
        """
        Bootstrap, create a virtualenv and install dependencies in it.

        :param recreate_venv: If True, delete the existing virtualenv before creating a new one.
            If False, do nothing if the virtualenv already exists.
        """
        self.create_virtualenv(recreate=recreate_venv)
        self.install_dependencies_in_virtualenv()


# project = Project.new(path_python="3.9")
# project = Project.new(path_python="python3.9")
# project = Project.new(path_python=str(Path.home().joinpath(".pyenv", "shims", "python3.9")))

# print(f"{project.path_python = !s}")
# print(f"{project.path_pip = !s}")
# print(f"{project.path_virtualenv = !s}")
# print(f"{project.dir_venv = !s}")
# print(f"{project.path_requirements_txt = !s}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="virtualenv_bootstrap",
        description="Create a virtualenv and install dependencies in it.",
    )
    parser.add_argument(
        "--path_python",
        help=(
            "the base Python interpreter for virtualenv, valid values are: "
            "3.9 (X.Y), python3.9 (pythonX.Y), /path/to/pythonX.Y"
        ),
    )
    parser.add_argument(
        "--dir_venv",
        help=(
            "the directory of virtualenv, there will be a ``bin`` "
            "directory in ``dir_venv``. If not specified, it will be the "
            "``.venv`` in the current working directory."
        ),
    )
    parser.add_argument(
        "--path_requirements_txt",
        help=(
            "the path to ``requirements.txt``, which "
            "contains the dependencies to be installed in the virtualenv. "
            "If not specified, it will be the ``requirements.txt`` in the "
            "current working directory."
        ),
    )

    args = parser.parse_args()

    # print(f"{args.path_python = !r}")
    # print(f"{args.dir_venv = !r}")
    # print(f"{args.path_requirements_txt = !r}")

    project = Project.new(
        path_python=args.path_python,
        dir_venv=args.dir_venv,
        path_requirements_txt=args.path_requirements_txt,
    )
    project.bootstrap()
