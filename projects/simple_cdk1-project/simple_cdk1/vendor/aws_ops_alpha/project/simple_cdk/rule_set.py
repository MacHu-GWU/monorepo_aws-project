# -*- coding: utf-8 -*-

from ...vendor import semantic_branch as sem_branch

from .simple_cdk_truth_table import SemanticBranchNameEnum

semantic_branch_rules = {
    SemanticBranchNameEnum.main: ["main", "master"],
    SemanticBranchNameEnum.feature: ["feature", "feat"],
    SemanticBranchNameEnum.fix: ["fix"],
    SemanticBranchNameEnum.doc: ["doc"],
    SemanticBranchNameEnum.app: ["app"],
    SemanticBranchNameEnum.release: ["release", "rls"],
    SemanticBranchNameEnum.cleanup: ["cleanup", "clean"],
}

semantic_branch_rule = sem_branch.SemanticBranchRule(
    rules=semantic_branch_rules,
)

google_sheet_url = "https://docs.google.com/spreadsheets/d/1OI3GXTUBtAbMyaLSnh_1S1X0jfTCBaFPIJLeRoP_uAY/edit#gid=58120413"
