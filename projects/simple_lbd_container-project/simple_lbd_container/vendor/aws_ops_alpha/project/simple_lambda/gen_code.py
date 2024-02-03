# -*- coding: utf-8 -*-

"""
This module helps developer to declare their own rule set for a specific project.
The declaration workflow are:

1. Define enum of ``conditions`` (dimension of the truth table).
2. Generate the initial truth table.
3. Manually update the truth table data.
4. Generate the ``${project_name}_truth_table.py`` Python module.

https://docs.google.com/spreadsheets/d/1OI3GXTUBtAbMyaLSnh_1S1X0jfTCBaFPIJLeRoP_uAY/edit#gid=238125239
"""

from pathlib import Path
import tt4human.api as tt4human
from aws_ops_alpha.rule_set import ConditionEnum, SHOULD_WE_DO_IT

project_name = "simple_lambda"

# 1. Define enum of ``conditions``
conditions = {
    ConditionEnum.step.value: [
        "CREATE_VIRTUALENV",
        "INSTALL_DEPENDENCIES",
        "DEPLOY_CONFIG",
        "BUILD_LAMBDA_SOURCE_LOCALLY",
        "RUN_CODE_COVERAGE_TEST",
        "BUILD_DOCUMENTATION",
        "UPDATE_DOCUMENTATION",
        "PUBLISH_LAMBDA_LAYER",
        "DEPLOY_CDK_STACK",
        "RUN_INTEGRATION_TEST",
        "PUBLISH_NEW_LAMBDA_VERSION",
        "CREATE_ARTIFACT_SNAPSHOT",
        "CREATE_GIT_TAG",
        "DELETE_CDK_STACK",
        "DELETE_ARTIFACT_SNAPSHOT",
        "DELETE_CONFIG",
    ],
    ConditionEnum.semantic_branch_name.value: [
        "main",
        "feature",
        "fix",
        "doc",
        "layer",
        "app",
        "release",
        "cleanup",
    ],
    ConditionEnum.runtime_name.value: [
        "local",
        "ci",
    ],
    ConditionEnum.env_name.value: [
        "devops",
        "sbx",
        "tst",
        "stg",
        "prd",
    ],
}

# 2. Generate the initial truth table.
dir_path = Path(__file__).absolute().parent
path_tsv = dir_path.joinpath(f"{SHOULD_WE_DO_IT}.tsv")
if path_tsv.exists() is False:
    tt4human.generate_initial_csv(
        conditions=conditions,
        flag_name=SHOULD_WE_DO_IT,
        path=path_tsv,
        overwrite=False,
    )

# 3. Manually update the truth table data.
# 4. Generate the ``${project_name}_truth_table.py`` Python module.
tt = tt4human.TruthTable.from_csv(path_tsv)
tt.generate_module(
    dir_path=dir_path,
    module_name=f"{project_name}_truth_table",
    overwrite=True,
)
