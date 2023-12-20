# -*- coding: utf-8 -*-

"""
This module implements the automation to maintain an importable Python library.

Developer note:

    every function in the ``workflow.py`` module should have visualized logging.
"""

# --- standard library
import typing as T

# --- third party library (include vendor)
import tt4human.api as tt4human
from ...vendor.emoji import Emoji

# --- modules from this project
from ...logger import logger
from ...multi_env.api import env_emoji_mapper
from ...runtime.api import runtime, runtime_emoji_mapper
from ...rule_set import should_we_do_it

# --- modules from this submodule
from .simple_python_truth_table import StepEnum, truth_table

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager


quiet = True if runtime.is_ci_runtime_group else False


def pip_install(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.pip_install(quiet=quiet, verbose=True)


def pip_install_dev(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.pip_install_dev(quiet=quiet, verbose=True)


def pip_install_test(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.pip_install_test(quiet=quiet, verbose=True)


def pip_install_doc(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.pip_install_doc(quiet=quiet, verbose=True)


def pip_install_automation(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.pip_install_automation(quiet=quiet, verbose=True)


def pip_install_all(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.pip_install_all(quiet=quiet, verbose=True)


def pip_install_all_in_ci(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    # if path_venv_bin_pytest already exists, it means that the virtualenv
    # is restored from cache, there's no need to install dependencies again.
    if pyproject_ops.path_venv_bin_pytest.exists() is False:
        pyproject_ops.pip_install_all(quiet=quiet, verbose=True)
    else:
        logger.info("dependencies are already installed, do nothing")


def poetry_lock(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.poetry_lock(verbose=True)


def poetry_export(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.poetry_export(verbose=True)


@logger.emoji_block(
    msg="Run Unit Test",
    emoji=Emoji.test,
)
def run_unit_test(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    check: bool = True,
    step: str = StepEnum.run_code_coverage_test.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
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
    pyproject_ops.run_unit_test()


@logger.emoji_block(
    msg="Run Code Coverage Test",
    emoji=Emoji.test,
)
def run_cov_test(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    check: bool = True,
    step: str = StepEnum.run_code_coverage_test.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
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
    pyproject_ops.run_cov_test()


def view_cov(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.view_cov(verbose=True)


@logger.emoji_block(
    msg="Run Unit Test",
    emoji=Emoji.test,
)
def run_int_test(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    check: bool = True,
    step: str = StepEnum.run_integration_test.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
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
    pyproject_ops.run_int_test()


@logger.emoji_block(
    msg="Build Documentation Site Locally",
    emoji=Emoji.doc,
)
def build_doc(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    check: bool = True,
    step: str = StepEnum.build_documentation.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
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

    pyproject_ops.build_doc()


def view_doc(pyproject_ops: "pyops.PyProjectOps"):  # pragma: no cover
    pyproject_ops.view_doc()


@logger.emoji_block(
    msg="Deploy Documentation Site To S3 as Versioned Doc",
    emoji=Emoji.doc,
)
def deploy_versioned_doc(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    bsm_devops: "BotoSesManager",
    bucket: str,
    prefix: str = "projects/",
    check: bool = True,
    step: str = StepEnum.update_documentation.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
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

    with bsm_devops.awscli():
        pyproject_ops.deploy_versioned_doc(bucket=bucket, prefix=prefix)


@logger.emoji_block(
    msg="Deploy Documentation Site To S3 as Latest Doc",
    emoji=Emoji.doc,
)
def deploy_latest_doc(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    bsm_devops: "BotoSesManager",
    bucket: str,
    prefix: str = "projects/",
    check: bool = True,
    step: str = StepEnum.update_documentation.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
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

    with bsm_devops.awscli():
        pyproject_ops.deploy_latest_doc(bucket=bucket, prefix=prefix)


def view_latest_doc(
    pyproject_ops: "pyops.PyProjectOps",
    bucket: str,
    prefix: str = "projects/",
):  # pragma: no cover
    pyproject_ops.view_latest_doc(bucket=bucket, prefix=prefix)


@logger.emoji_block(
    msg="Show context info",
    emoji=Emoji.eye,
)
def show_context_info(
    git_branch_name: str,
    runtime_name: str,
    env_name: str,
    git_commit_id: T.Optional[str] = None,
    git_commit_message: T.Optional[str] = None,
):  # pragma: no cover
    git_commit_id = git_commit_id or "❓"
    git_commit_message = git_commit_message or "❓"
    logger.info(f"Current git branch is 🔀 {git_branch_name!r}")
    logger.info(f"Current git commit is ✅ {git_commit_id!r}")
    logger.info(f"Current git commit message is ✅ {git_commit_message!r}")
    runtime_emoji = runtime_emoji_mapper.get(runtime_name, "❓")
    logger.info(f"Current runtime is {runtime_emoji} {runtime_name!r}")
    env_emoji = env_emoji_mapper.get(env_name, "❓")
    logger.info(f"Current environment name is {env_emoji} {env_name!r}")


@logger.emoji_block(
    msg="bump version",
    emoji=Emoji.label,
)
def bump_version(
    pyproject_ops: "pyops.PyProjectOps",
    major: bool = False,
    minor: bool = False,
    patch: bool = False,
    minor_start_from: int = 0,
    micro_start_from: int = 0,
):  # pragma: no cover
    pyproject_ops.bump_version(
        major=major,
        minor=minor,
        patch=patch,
        minor_start_from=minor_start_from,
        micro_start_from=micro_start_from,
    )
