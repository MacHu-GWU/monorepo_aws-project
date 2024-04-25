# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``step.py`` module should have visualized logging.
"""

# --- standard library
import typing as T
from pathlib import Path

# --- third party library (include vendor)
from config_patterns.logger import logger as config_patterns_logger
import tt4human.api as tt4human
from ...vendor.emoji import Emoji

# --- modules from this project
from ...logger import logger
from ...constants import CommonEnvNameEnum
from ...runtime.api import Runtime
from ...multi_env.api import BaseEnvNameEnum
from ...config.api import BaseConfig, BaseEnv, T_BASE_CONFIG
from ...rule_set import should_we_do_it

# --- modules from this submodule
from .simple_config_truth_table import StepEnum, truth_table

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


# fmt: off
@logger.emoji_block(
    msg="Deploy Config",
    emoji=Emoji.config,
)
def deploy_config(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
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
    step: str = StepEnum.deploy_config.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
# fmt: on
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
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
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
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
    step: str = StepEnum.delete_config.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
# fmt: on
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
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
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    runtime: Runtime,
    bsm_devops: "BotoSesManager",
    env_name_enum_class: T.Union[BaseEnvNameEnum, T.Type[BaseEnvNameEnum]],
    env_class: T.Type[BaseEnv],
    config_class: T.Type[BaseConfig],
    version: str,
    path_config_json: T.Optional[Path] = None,
    path_config_secret_json: T.Optional[Path] = None,
    check: bool = True,
    step: str = StepEnum.create_config_snapshot.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    logger.info(
        f"Now we are in {env_name!r}, "
        f"Create Config Snapshot in {CommonEnvNameEnum.devops.value!r} environment ..."
    )
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return

    s3path, flag = config_class.smart_backup(
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
