# -*- coding: utf-8 -*-

"""
Define the Git repo and Git semantic branch setup for this project.
"""

from .vendor.import_agent import aws_ops_alpha
from .paths import dir_project_root

# we use MonoRepo to manage all deployment units.
git_repo = aws_ops_alpha.MonoGitRepo(
    dir_repo=dir_project_root.parent.parent,
    sem_branch_rule=aws_ops_alpha.simple_lambda_project.semantic_branch_rule,
)
