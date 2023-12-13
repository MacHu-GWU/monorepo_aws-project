# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``workflow.py`` module should have visualized logging.
"""

# standard library
import typing as T
from pathlib import Path

# third party library (include vendor)
from config_patterns.logger import logger as config_patterns_logger
from ...vendor.emoji import Emoji
from ...vendor import semantic_branch as sem_branch


# modules from this project
from ...logger import logger
from ...runtime import Runtime
from ...environment import BaseEnvNameEnum
from ...config.api import BaseConfig, BaseEnv, T_BASE_CONFIG


# modules from this submodule
from .constants import StepEnum, GitBranchNameEnum
from .rule import RuleSet, rule_set as default_rule_set

# type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager


semantic_branch_rules = {
    GitBranchNameEnum.main: ["main", "master"],
    GitBranchNameEnum.release: ["release", "rls"],
}

semantic_branch_rule = sem_branch.SemanticBranchRule(
    rules=semantic_branch_rules,
)

# fmt: off
@logger.emoji_block(
    msg="Deploy Config",
    emoji=Emoji.config,
)
def deploy_config(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    config: T_BASE_CONFIG,
    bsm: T.Union[
        "BotoSesManager",
        T.Dict[str, "BotoSesManager"],
    ],
    parameter_with_encryption: T.Optional[bool] = None,
    s3folder_config: T.Optional[
        T.Union[
            str,
            T.Dict[str, str],
        ]
    ] = None,
    check: bool = True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
# fmt: on
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.CREATE_CONFIG_SNAPSHOT,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    with config_patterns_logger.nested():
        config.deploy(
            bsm=bsm,
            parameter_with_encryption=parameter_with_encryption,
            s3folder_config=s3folder_config,
            verbose=True,
        )


# fmt: off
@logger.emoji_block(
    msg="Deploy Config",
    emoji=Emoji.config,
)
def delete_config(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    config: T_BASE_CONFIG,
    bsm: T.Union[
        "BotoSesManager",
        T.Dict[str, "BotoSesManager"],
    ],
    use_parameter_store: T.Optional[bool] = None,
    s3folder_config: T.Optional[
        T.Union[
            str,
            T.Dict[str, str],
        ]
    ] = None,
    include_history: bool = False,
    check: bool = True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
# fmt: on
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.CREATE_CONFIG_SNAPSHOT,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    with config_patterns_logger.nested():
        config.delete(
            bsm=bsm,
            use_parameter_store=use_parameter_store,
            s3folder_config=s3folder_config,
            include_history=include_history,
            verbose=True,
        )


@logger.emoji_block(
    msg="Create Config Snapshot",
    emoji=Emoji.config,
)
def create_config_snapshot(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    runtime: Runtime,
    bsm_devops: "BotoSesManager",
    env_name_enum_class: T.Union[BaseEnvNameEnum, T.Type[BaseEnvNameEnum]],
    env_class: T.Type[BaseEnv],
    config_class: T.Type[BaseConfig],
    version: str,
    path_config_json: T.Optional[Path] = None,
    path_config_secret_json: T.Optional[Path] = None,
    check: bool = True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
    logger.info(f"Create Config Snapshot in {env_name!r} env...")
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.CREATE_CONFIG_SNAPSHOT,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    s3path = config_class.smart_backup(
        runtime=runtime,
        bsm_devops=bsm_devops,
        env_name_enum_class=env_name_enum_class,
        env_class=env_class,
        version=version,
        path_config_json=path_config_json,
        path_config_secret_json=path_config_secret_json,
    )

    logger.info(f"config snapshot is saved to {s3path.uri}")
    logger.info(f"preview it at: {s3path.console_url}")
