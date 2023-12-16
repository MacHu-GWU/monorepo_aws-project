# -*- coding: utf-8 -*-

"""
.. note::

    This module has to be run in virtualenv Python
"""

import typing as T
import os
import shutil
import subprocess
import importlib
from pathlib import Path

from cookiecutter_maker.maker import Maker

from . import paths


def _new_project(
    dir_seed_project: Path,
    mapper: T.List[T.Tuple[str, str, str]],
    exclude: T.List[str],
):
    """
    Create a new project based on a seed project.

    Seed projects are only different in the following aspects:

    1. The seed project folder location.
    2. list of string you want to convert them to a variable (i.e. the mapper).
    3. list of files to ignore.

    You can find more details at https://github.com/MacHu-GWU/cookiecutter_maker-project
    """
    print(f"📋 Convert {dir_seed_project} into a template project ...")
    shutil.rmtree(paths.dir_tmp, ignore_errors=True)
    maker = Maker.new(
        input_dir=f"{dir_seed_project}",
        output_dir=f"{paths.dir_template_project}",
        mapper=mapper,
        include=[],
        exclude=exclude,
        overwrite=True,
        ignore_mapper_error=False,
        skip_mapper_prompt=False,
        debug=False,
    )
    maker.templaterize(cleanup_output_dir=True)

    print(f"🐍 Generate a new project from template project ...")
    os.chdir(f"{paths.dir_template_project}")
    args = [
        f"{paths.path_bin_cookiecutter}",
        ".",
    ]
    subprocess.run(args, check=True)

    print(f"preview your project code skeleton at {paths.dir_template_project}")


def new_project(
    seed: str,
):
    """
    Create a new project based on a seed project.

    It imports the ``dir_seed_project, mapper, exclude`` from the ``pylib.seeds.${seed}``
    module and call the :func:`_new_project` function.
    """
    print(f"🚀 Create a new project like {seed!r}")
    module = importlib.import_module(f"pylib.seeds.{seed}")
    _new_project(
        dir_seed_project=module.dir_seed_project,
        mapper=module.mapper,
        exclude=module.exclude,
    )
