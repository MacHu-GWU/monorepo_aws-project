# -*- coding: utf-8 -*-

"""
Usage example:

    >>> import aws_ops_alpha.api as aws_ops_alpha
    >>> aws_ops_alpha.runtime
    ...
    >>> aws_ops_alpha.get_devops_aws_account_id_in_ci()
    ...
    >>> aws_ops_alpha.get_workload_aws_account_id_in_ci("sbx")
    ...
"""

from .config import Config
from .runtime import Runtime
from .runtime import RunTimeEnum
from .runtime import runtime
from .env_var import get_devops_aws_account_id_in_ci
from .env_var import get_workload_aws_account_id_in_ci
from .boto_ses import BotoSesFactory
from .rule import only_execute_on_certain_runtime
from .rule import only_execute_on_certain_branch
from .rule import only_execute_on_certain_env
from .rule import log_why_not_run_integration_test_in_prod
from .rule import confirm_to_proceed_in_prod
from .rule import only_execute_on_certain_runtime_branch_env
from .rule import log_why_not_create_git_tag_in_non_prod
from .rule import log_why_not_create_git_tag_in_local
from .logger import logger
from .emoji import Emoji
from . import constants
from .workflow import simple_lambda
