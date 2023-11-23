# -*- coding: utf-8 -*-

"""
This module automates dependencies management.

We use `Python poetry <https://python-poetry.org/>`_ to ensure determinative dependencies.
"""

from .pyproject import pyproject_ops
from .logger import logger
from .emoji import Emoji
from .runtime import IS_CI


quiet = True if IS_CI else False


@logger.start_and_end(
    msg="Resolve Dependencies Tree",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def poetry_lock():
    pyproject_ops.poetry_lock()


@logger.start_and_end(
    msg="Install main dependencies and Package itself",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def poetry_install():
    pyproject_ops.poetry_install()


@logger.start_and_end(
    msg="Install dev dependencies",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def poetry_install_dev():
    pyproject_ops.poetry_install_dev()


@logger.start_and_end(
    msg="Install test dependencies",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def poetry_install_test():
    pyproject_ops.poetry_install_test()


@logger.start_and_end(
    msg="Install doc dependencies",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def poetry_install_doc():
    pyproject_ops.poetry_install_doc()


@logger.start_and_end(
    msg="Install all dependencies for dev, test, doc",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def poetry_install_all():
    pyproject_ops.poetry_install_all()


@logger.start_and_end(
    msg="Export resolved dependencies to req-***.txt file",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def poetry_export():
    flag = pyproject_ops.poetry_export()
    if flag is False:
        logger.info("already did, do nothing")


@logger.start_and_end(
    msg="Install main dependencies and Package itself",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def pip_install():
    pyproject_ops.pip_install(quiet=quiet)


@logger.start_and_end(
    msg="Install dev dependencies",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def pip_install_dev():
    pyproject_ops.pip_install_dev(quiet=quiet)


@logger.start_and_end(
    msg="Install test dependencies",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def pip_install_test():
    pyproject_ops.pip_install_test(quiet=quiet)


@logger.start_and_end(
    msg="Install doc dependencies",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def pip_install_doc():
    pyproject_ops.pip_install_doc(quiet=quiet)


@logger.start_and_end(
    msg="Install automation dependencies",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def pip_install_automation():
    pyproject_ops.pip_install_automation(quiet=quiet)


@logger.start_and_end(
    msg="Install all dependencies",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def pip_install_all():
    pyproject_ops.pip_install_all(quiet=quiet)
