# -*- coding: utf-8 -*-

import typing as T
import importlib

import fire
from pathlib import Path


class Command:
    """
    AWS Ops Alpha
    """

    def __call__(self, version: bool = False):
        if version:
            from ._version import __version__

            print(__version__)
            return

        print("type aws_ops_alpha -h for help")

    def display(self, name: T.Optional[str] = None):
        """
        Display the rule set of the given project type name.

        For example: aws_ops_alpha display simple_python
        """
        if name is None:
            dir_here = Path(__file__).absolute().parent
            dir_workflow = dir_here / "workflow"
            name_list = list()
            for dir_folder in dir_workflow.iterdir():
                if dir_folder.is_dir():
                    if dir_folder.joinpath("api.py").exists():
                        name_list.append(dir_folder.name)
            print(
                f"run 'aws_ops_alpha display <name>' to print rule set "
                f"for the given name, examples:"
            )
            for name in name_list:
                print(f"aws_ops_alpha display {name}")
            return
        importlib.import_module(f"aws_ops_alpha.workflow.{name}.api").rule_set.display()


def main():
    fire.Fire(Command())
