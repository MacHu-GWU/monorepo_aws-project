# -*- coding: utf-8 -*-

"""
Config data related.
"""

import typing as T

from .runtime import IS_LOCAL, CURRENT_RUNTIME
from .logger import logger
from .emoji import Emoji
from .config_rule import do_we_deploy_config, do_we_delete_config

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager
    from config_patterns import api as config_patterns


@logger.start_and_end(
    msg="Deploy Config",
    start_emoji=Emoji.deploy,
    error_emoji=f"{Emoji.failed} {Emoji.deploy}",
    end_emoji=f"{Emoji.succeeded} {Emoji.deploy}",
    pipe=Emoji.deploy,
)
def deploy_config(
    config: "config_patterns.multi_env_json.BaseConfig",
    bsm: "BotoSesManager",
    check: bool = True,
):
    """
    Deploy config data to parameter store backend.
    """
    if check:
        if (
            do_we_deploy_config(
                is_local_runtime=IS_LOCAL,
                runtime_name=CURRENT_RUNTIME,
            )
            is False
        ):
            return
    config.deploy(bsm=bsm, parameter_with_encryption=True)


@logger.start_and_end(
    msg="Delete Config",
    start_emoji=Emoji.delete,
    error_emoji=f"{Emoji.failed} {Emoji.delete}",
    end_emoji=f"{Emoji.succeeded} {Emoji.delete}",
    pipe=Emoji.delete,
)
def delete_config(
    config: "config_patterns.multi_env_json.BaseConfig",
    bsm: "BotoSesManager",
    check: bool = True,
):
    """
    Delete config data from parameter store backend.
    """
    if check:
        if (
            do_we_delete_config(
                is_local_runtime=IS_LOCAL,
                runtime_name=CURRENT_RUNTIME,
            )
            is False
        ):
            return
    config.delete(bsm=bsm, use_parameter_store=True)
