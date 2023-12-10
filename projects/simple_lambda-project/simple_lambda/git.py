# -*- coding: utf-8 -*-

import aws_ops_alpha.api as aws_ops_alpha
from .paths import dir_project_root

git_repo = aws_ops_alpha.MonoGitRepo(
    dir_repo=dir_project_root.parent.parent,
    sem_branch_rule=aws_ops_alpha.simple_lambda_project.semantic_branch_rule,
)
