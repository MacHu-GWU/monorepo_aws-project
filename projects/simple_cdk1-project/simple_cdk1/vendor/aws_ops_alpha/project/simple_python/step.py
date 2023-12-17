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
from ...runtime.api import runtime
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
        pyproject_ops.deploy_versioned_doc(bucket=bucket)


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
        pyproject_ops.deploy_latest_doc(bucket=bucket)


def view_latest_doc(
    pyproject_ops: "pyops.PyProjectOps",
    bucket: str,
):  # pragma: no cover
    pyproject_ops.view_latest_doc(bucket=bucket)
