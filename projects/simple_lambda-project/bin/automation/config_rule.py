# -*- coding: utf-8 -*-

from .logger import logger
from .emoji import Emoji


def do_we_deploy_config(
    is_local_runtime: bool,
    runtime_name: str,
) -> bool:
    """
    Check if we should deploy config to parameter store / S3 backend.
    """
    # always allow deploy config on local
    if is_local_runtime:
        return True
    else:
        logger.info(
            f"{Emoji.red_circle} we only deploy config from local laptop!"
            f"now it is {runtime_name!r} runtime."
        )
        return False


def do_we_delete_config(
    is_local_runtime: bool,
    runtime_name: str,
) -> bool:
    """
    Check if we should delete config from parameter store / S3 backend.
    """
    if is_local_runtime is False:
        logger.info(
            f"{Emoji.red_circle} we only delete config from local laptop!"
            f"now it is {runtime_name!r} runtime."
        )
        return False
    user_input = input(
        f"you are trying to delete all config history, this can not be undone,"
        f"enter 'YES' to confirm: "
    )
    if user_input.strip() == "YES":
        return True
    else:
        logger.info(
            f"{Emoji.red_circle} don't deploy app. "
            f"because user input {user_input!r} is not 'YES'."
        )
        return False
