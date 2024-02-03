# -*- coding: utf-8 -*-

"""
Environment variables utilities.

Usage::

    from fixa.env_var import (
        temp_env_var,
        normalize_env_var_name,
    )
"""

import typing as T
import os
import contextlib

__version__ = "0.1.1"


@contextlib.contextmanager
def temp_env_var(mapper: T.Dict[str, str]):
    """
    Temporarily set environment variables and revert them back.

    .. versionadded:: 0.1.1
    """
    # get existing env var
    existing = {}
    for k, v in mapper.items():
        existing[k] = os.environ.get(k)

    try:
        # set new env var
        for k, v in mapper.items():
            os.environ[k] = v
        yield
    finally:
        # recover the original env var
        for k, v in existing.items():
            if v is None:
                os.environ.pop(k)
            else:
                os.environ[k] = v


def normalize_env_var_name(name: str) -> str:
    """
    In Google Style guide, constants and environment variable names should be
    All caps, separated with underscores.

    This function convert a string to a valid environment variable name.

    Reference:

    - https://google.github.io/styleguide/shellguide.html#constants-and-environment-variable-names

    .. versionadded:: 0.1.1
    """
    return name.upper().replace("-", "_").replace(" ", "_")
