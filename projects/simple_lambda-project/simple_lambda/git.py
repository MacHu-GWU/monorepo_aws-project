# -*- coding: utf-8 -*-

from .vendor.aws_ops_alpha.git import GitRepo
from .paths import dir_project_root

git_repo = GitRepo(dir_project_root.parent.parent)
