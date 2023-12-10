# -*- coding: utf-8 -*-

from aws_ops_alpha.git import MonoGitRepo
from .paths import dir_project_root

git_repo = MonoGitRepo(dir_project_root.parent.parent)
