# -*- coding: utf-8 -*-

"""
This module helps developer to declare their own rule set for a specific project.
The declaration workflow are:

1. Define enum of ``conditions`` (dimension of the truth table).
2. Generate the initial truth table.
3. Manually update the truth table data.
4. Generate the ``${project_name}_truth_table.py`` Python module.

https://docs.google.com/spreadsheets/d/1OI3GXTUBtAbMyaLSnh_1S1X0jfTCBaFPIJLeRoP_uAY/edit#gid=58120413
"""

from pathlib import Path
import tt4human.api as tt4human
from aws_ops_alpha.rule_set import ConditionEnum, SHOULD_WE_DO_IT

project_name = "simple_config"

# 1. Define enum of ``conditions``
conditions = {
    ConditionEnum.step.value: [
        "DEPLOY_CONFIG",
        "CREATE_CONFIG_SNAPSHOT",
        "DELETE_CONFIG",
    ],
    ConditionEnum.semantic_branch_name.value: [
        "main",
        "release",
    ],
    ConditionEnum.runtime_name.value: [
        "local",
        "ci",
    ],
    ConditionEnum.env_name.value: [
        "devops",
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
