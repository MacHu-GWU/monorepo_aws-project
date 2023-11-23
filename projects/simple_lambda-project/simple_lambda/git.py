# -*- coding: utf-8 -*-

import os

from fixa.git_cli import get_git_commit_id_from_git_cli, GitCLIError

from .paths import dir_project_root
from .runtime import IS_LOCAL, IS_CI


if IS_LOCAL:
    try:
        git_commit_id = get_git_commit_id_from_git_cli(
            dir_repo=dir_project_root.parent.parent
        )
    except GitCLIError:
        git_commit_id = "unknown in local"
elif IS_CI:
    if "USER_GIT_COMMIT_ID" in os.environ:
        git_commit_id = os.environ["USER_GIT_COMMIT_ID"]
    elif "CODEBUILD_RESOLVED_SOURCE_VERSION" in os.environ:
        git_commit_id = os.environ["CODEBUILD_RESOLVED_SOURCE_VERSION"]
    else:
        git_commit_id = "unknown in CI"
else:
    raise NotImplementedError
