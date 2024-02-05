# -*- coding: utf-8 -*-

from ...vendor import semantic_branch as sem_branch

from .simple_lambda_truth_table import SemanticBranchNameEnum

semantic_branch_rules = {
    SemanticBranchNameEnum.main.value: ["main", "master"],
    SemanticBranchNameEnum.feature.value: ["feature", "feat"],
    SemanticBranchNameEnum.fix.value: ["fix"],
    SemanticBranchNameEnum.doc.value: ["doc"],
    SemanticBranchNameEnum.layer.value: ["layer"],
    SemanticBranchNameEnum.app.value: ["app"],
    SemanticBranchNameEnum.release.value: ["release", "rls"],
    SemanticBranchNameEnum.cleanup.value: ["cleanup", "clean"],
}

semantic_branch_rule = sem_branch.SemanticBranchRule(
    rules=semantic_branch_rules,
)

google_sheet_url = "https://docs.google.com/spreadsheets/d/1OI3GXTUBtAbMyaLSnh_1S1X0jfTCBaFPIJLeRoP_uAY/edit#gid=238125239"
