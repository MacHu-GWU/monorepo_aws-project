# -*- coding: utf-8 -*-

from .logger import logger
from .emoji import Emoji


def do_we_build_lambda_layer(
    is_ci_runtime: bool,
    branch_name: str,
    is_layer_branch: bool,
) -> bool:
    """
    This function defines the rule of whether we build Lambda layer or not.
    """
    if is_ci_runtime:  # in CI, we only build layer from layer branch
        if is_layer_branch:
            pass
        else:
            logger.info(
                f"{Emoji.red_circle} don't build Lambda layer, "
                f"we only build layer from CI environment on a 'layer' branch, "
                f"now we are on {branch_name!r} branch."
            )
            return False
    else:  # always allow build layer on local
        return True
