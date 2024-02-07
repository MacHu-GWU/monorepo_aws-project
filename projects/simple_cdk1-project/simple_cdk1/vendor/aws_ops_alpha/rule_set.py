# -*- coding: utf-8 -*-

"""
This module is a wrapper of the
`tt4human <https://pypi.org/project/tt4human/>`_ that provide additional feature
specifically for aws_ops_alpha project.
"""

import typing as T

import tt4human.api as tt4human
from .vendor.emoji import Emoji

from .logger import logger


class ConditionEnum(tt4human.BetterStrEnum):
    """
    In aws_ops_alpha, we have a set of conditions that we want to check
    """

    step = "step"
    semantic_branch_name = "semantic_branch_name"
    runtime_name = "runtime_name"
    env_name = "env_name"


SHOULD_WE_DO_IT = "should_we_do_it"


def encode_case(case: T.Dict[str, str]) -> str:
    return ", ".join([f"{k} = {v!r}" for k, v in case.items()])


def should_we_do_it(
    step: str,
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    truth_table: tt4human.TruthTable,
    google_sheet_url: T.Optional[str] = None,
    verbose: bool = True,
) -> bool:
    """
    Get the boolean flag value to identify whether we should run a step
    under the condition of semantic branch name, runtime name, and env name.

    if evaluation result is False, it will print the reason why it is False.

    :param step: step name for conditional step test
    :param semantic_branch_name: semantic branch name for conditional step test
    :param runtime_name: runtime name for conditional step test
    :param env_name: env name for conditional step test
    :param truth_table: truth table for conditional step test
    :param google_sheet_url: print the Google sheet url when conditional step test failed

    :return bool: True if we should run the step, False if we should not run the step.
    """
    case = {
        ConditionEnum.step.value: step,
        ConditionEnum.semantic_branch_name.value: semantic_branch_name,
        ConditionEnum.runtime_name.value: runtime_name,
        ConditionEnum.env_name.value: env_name,
    }
    flag = truth_table.evaluate(case=case)

    if flag is False:
        with logger.disabled(
            disable=not verbose,
        ):
            logger.info(
                f"{Emoji.red_circle} don't do {step!r} when {encode_case(case)}"
            )
            if google_sheet_url:
                logger.info(f"you can view the truth table at {google_sheet_url}")
            logger.info(f"below are valid cases to do {step!r}:")
            for row in truth_table.rows:
                dct = dict(zip(truth_table.headers, row))
                if (
                    dct[ConditionEnum.step.value] == step
                    and dct[SHOULD_WE_DO_IT] is True
                ):
                    dct.pop(SHOULD_WE_DO_IT)
                    logger.info(f"- {encode_case(dct)}")

    return flag
