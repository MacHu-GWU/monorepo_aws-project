# -*- coding: utf-8 -*-

from ...vendor import semantic_branch as sem_branch

from .simple_python_truth_table import SemanticBranchNameEnum

semantic_branch_rules = {
    SemanticBranchNameEnum.main.value: ["main", "master"],
    SemanticBranchNameEnum.feature.value: ["feature", "feat"],
    SemanticBranchNameEnum.fix.value: ["fix"],
    SemanticBranchNameEnum.doc.value: ["doc"],
    SemanticBranchNameEnum.test.value: ["test"],
    SemanticBranchNameEnum.release.value: ["release", "rls"],
}

semantic_branch_rule = sem_branch.SemanticBranchRule(
    rules=semantic_branch_rules,
)

google_sheet_url = "https://docs.google.com/spreadsheets/d/1OI3GXTUBtAbMyaLSnh_1S1X0jfTCBaFPIJLeRoP_uAY/edit#gid=1959601496"
