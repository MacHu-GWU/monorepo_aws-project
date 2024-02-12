# -*- coding: utf-8 -*-

"""
Usage example:

    >>> import aws_ops_alpha.api as aws_ops_alpha
    >>> aws_ops_alpha.runtime
    ...
"""

# ordered from the module having the least dependencies to the one having most dependencies
from . import constants
from .logger import logger
from .constants import CommonEnvNameEnum
from .constants import EnvVarNameEnum
from .constants import AwsTagNameEnum
from .constants import AwsOpsSemanticBranchEnum
from .env_var import temp_env_var
from .env_var import normalize_env_var_name
from .env_var import get_environment_aws_account_id_in_ci
from .env_var import get_environment_iam_role_arn_in_dev_server
from .env_var import temp_env_var
from .runtime.api import RunTimeGroupEnum
from .runtime.api import RunTimeEnum
from .runtime.api import Runtime
from .runtime.api import runtime
from .multi_env.api import EnvNameValidationError
from .multi_env.api import validate_env_name
from .multi_env.api import BaseEnvNameEnum
from .multi_env.api import env_emoji_mapper
from .multi_env.api import EnvNameEnum
from .multi_env.api import detect_current_env
from .git.api import InvalidSemanticNameError
from .git.api import SemanticBranchRule
from .git.api import GitRepo
from .git.api import extract_semantic_branch_name_for_multi_repo
from .git.api import extract_semantic_branch_name_for_mono_repo
from .git.api import MultiGitRepo
from .git.api import MonoGitRepo
from .boto_ses.api import AbstractBotoSesFactory
from .boto_ses.api import AlphaBotoSesFactory
from .config.api import BaseConfig
from .config.api import BaseEnv
from .config.api import T_BASE_CONFIG
from .config.api import T_BASE_ENV
from .vendor import aws_lambda_version_and_alias
from .vendor import aws_stepfunction_version_and_alias

# user may not need some features to write their application code
# these features are typically used in CI/CD and devops only
# so we just try to import them here, if we are missing dependencies,
# we skip import them
try:
    from .aws_helpers.api import python_helpers
except ImportError: # pragma: no cover
    pass
try:
    from .aws_helpers.api import aws_cdk_helpers
except ImportError: # pragma: no cover
    pass
try:
    from .aws_helpers.api import aws_lambda_helpers
except ImportError: # pragma: no cover
    pass
try:
    from .aws_helpers.api import aws_ecr_helpers
except ImportError: # pragma: no cover
    pass
try:
    from .aws_helpers.api import aws_chalice_helpers
except ImportError: # pragma: no cover
    pass
try:
    from .aws_helpers.api import aws_glue_helpers
except ImportError: # pragma: no cover
    pass
try:
    from .aws_helpers.api import rich_helpers
except ImportError: # pragma: no cover
    pass

try:
    from .project.api import simple_python_project
except ImportError: # pragma: no cover
    pass
try:
    from .project.api import simple_cdk_project
except ImportError: # pragma: no cover
    pass
try:
    from .project.api import simple_config_project
except ImportError: # pragma: no cover
    pass
try:
    from .project.api import simple_lambda_project
except ImportError: # pragma: no cover
    pass
try:
    from .project.api import simple_lbd_container_project
except ImportError: # pragma: no cover
    pass
try:
    from .project.api import simple_lbd_agw_chalice_project
except ImportError: # pragma: no cover
    pass
try:
    from .project.api import simple_glue_project
except ImportError: # pragma: no cover
    pass
try:
    from .project.api import simple_sfn_project
except ImportError: # pragma: no cover
    pass

try:
    from .boostrap import api as boostrap
except ImportError:  # pragma: no cover
    pass
