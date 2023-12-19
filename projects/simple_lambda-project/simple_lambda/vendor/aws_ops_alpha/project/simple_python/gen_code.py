# -*- coding: utf-8 -*-

"""
https://docs.google.com/spreadsheets/d/1OI3GXTUBtAbMyaLSnh_1S1X0jfTCBaFPIJLeRoP_uAY/edit#gid=58120413
"""

from pathlib import Path
import tt4human.api as tt4human
from aws_ops_alpha.rule_set import ConditionEnum, SHOULD_WE_DO_IT

project_name = "simple_python"

conditions = {
    ConditionEnum.step.value: [
        "CREATE_VIRTUALENV",
        "INSTALL_DEPENDENCIES",
        "BUILD_SOURCE_CODE",
        "RUN_CODE_COVERAGE_TEST",
        "BUILD_DOCUMENTATION",
        "UPDATE_DOCUMENTATION",
        "RUN_INTEGRATION_TEST",
        "PUBLISH_PACKAGE",
    ],
    ConditionEnum.semantic_branch_name.value: [
        "main",
        "feature",
        "fix",
        "doc",
        "test",
        "release",
    ],
    ConditionEnum.runtime_name.value: [
        "local",
        "ci",
    ],
    ConditionEnum.env_name.value: [
        "devops",
        "sbx",
    ],
}

dir_path = Path(__file__).absolute().parent
path_tsv = dir_path.joinpath(f"{SHOULD_WE_DO_IT}.tsv")
if path_tsv.exists() is False:
    tt4human.generate_initial_csv(
        conditions=conditions,
        flag_name=SHOULD_WE_DO_IT,
        path=path_tsv,
        overwrite=False,
    )

tt = tt4human.TruthTable.from_csv(path_tsv)
tt.generate_module(
    dir_path=dir_path,
    module_name=f"{project_name}_truth_table",
    overwrite=True,
)
