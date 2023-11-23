# -*- coding: utf-8 -*-

"""
Virtualenv management.
"""

from .pyproject import pyproject_ops
from .logger import logger
from .emoji import Emoji


@logger.start_and_end(
    msg="Create Virtual Environment",
    start_emoji=Emoji.python,
    error_emoji=f"{Emoji.failed} {Emoji.python}",
    end_emoji=f"{Emoji.succeeded} {Emoji.python}",
    pipe=Emoji.python,
)
def create_virtualenv():
    flag = pyproject_ops.create_virtualenv()
    if flag:
        logger.info("done")
    else:
        logger.info(f"{pyproject_ops.dir_venv} already exists, do nothing.")


@logger.start_and_end(
    msg="Remove Virtual Environment",
    start_emoji=Emoji.python,
    error_emoji=f"{Emoji.failed} {Emoji.python}",
    end_emoji=f"{Emoji.succeeded} {Emoji.python}",
    pipe=Emoji.python,
)
def remove_virtualenv():
    """
    .. code-block:: bash

        $ rm -r ./.venv
    """
    flag = pyproject_ops.remove_virtualenv()
    if flag:
        logger.info(f"done! {pyproject_ops.dir_venv} is removed.")
    else:
        logger.info(f"{pyproject_ops.dir_venv} doesn't exists, do nothing.")
