# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``step.py`` module should have visualized logging.
"""

# --- standard library
import typing as T

# --- third party library (include vendor)
import aws_console_url.api as aws_console_url
import tt4human.api as tt4human
from ...vendor.aws_stepfunction_version_and_alias import (
    publish_version,
    deploy_alias,
)

# --- modules from this project
from ...logger import logger
from ...rule_set import should_we_do_it

# --- modules from this submodule
from .simple_sfn_truth_table import StepEnum, truth_table

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


@logger.emoji_block(
    msg="Publish new State Machine version",
    emoji="🎰",
)
def publish_state_machine_version(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_workload: "BotoSesManager",
    state_machine_name_list: T.List[str],
    check: bool = True,
    step: str = StepEnum.publish_new_state_machine_version.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Publish a new State Machine version from latest.

    .. note::

        as of 2024-02, AWS CDK doesn't support to manage StateMachine
        versions and alias automatically. So we need to publish new version manually.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_workload: the workload AWS Account ``BotoSesManager`` object.
    :param state_machine_name_list: list of state machine names.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
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

    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    for state_machine_name in state_machine_name_list:
        url = aws_console.step_function.get_state_machine_view_tab(state_machine_name)
        logger.info(f"preview State Machine {state_machine_name!r}: {url}", 1)
        # StepFunctions doesn’t publish a version if the state machine’s configuration
        # and definition haven’t changed since the last version.
        publish_version(
            sfn_client=bsm_workload.sfn_client,
            state_machine_arn=aws_console.step_function.get_state_machine_arn(
                name=state_machine_name,
            ),
        )


@logger.emoji_block(
    msg="Deploy State Machine Alias",
    emoji="🎰",
)
def deploy_state_machine_alias(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_workload: "BotoSesManager",
    state_machine_name: str,
    alias: str,
    version1: T.Optional[str] = None,
    version2: T.Optional[str] = None,
    version2_percentage: T.Optional[int] = None,
    check: bool = True,
    step: str = StepEnum.publish_new_state_machine_version.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Deploy State Machine alias.

    .. note::

        as of 2024-02, AWS CDK doesn't support to manage StateMachine
        versions and alias automatically. So we need to publish new version manually.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_workload: the workload AWS Account ``BotoSesManager`` object.
    :param state_machine_name: state machine name.
    :param alias: alias name.
    :param version1: the main version of the alias; if not specified, use $LATEST
    :param version2: the secondary version of the alias; if not specified, then
        the version1 will have 100% traffic; if specified, then version2_percentage
        also has to be specified.
    :param version2_percentage: if version2 is specified, then it has to be a
        value between 1 - 99.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
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

    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    arn = aws_console.step_function.get_state_machine_arn(state_machine_name)
    url = aws_console.step_function.get_state_machine_view_tab(state_machine_name)
    logger.info(f"preview State Machine {state_machine_name!r}: {url}", 1)
    deploy_alias(
        sfn_client=bsm_workload.sfn_client,
        state_machine_arn=arn,
        alias=alias,
        version1=version1,
        version2=version2,
        version2_percentage=version2_percentage,
    )
