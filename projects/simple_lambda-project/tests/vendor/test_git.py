# -*- coding: utf-8 -*-

from simple_lambda.paths import dir_project_root
from simple_lambda.vendor.aws_ops_alpha.git import GitRepo


class TestGitRepo:
    def test(self):
        git_repo = GitRepo(dir_project_root.parent.parent)

        _ = git_repo.git_branch_name
        _ = git_repo.git_commit_id
        _ = git_repo.git_commit_message
        _ = git_repo.semantic_branch_name
        _ = git_repo.is_main_branch
        _ = git_repo.is_feature_branch
        _ = git_repo.is_fix_branch
        _ = git_repo.is_doc_branch
        _ = git_repo.is_release_branch
        _ = git_repo.is_cleanup_branch
        _ = git_repo.is_lambda_branch
        _ = git_repo.is_layer_branch
        _ = git_repo.is_ecr_branch
        _ = git_repo.is_ami_branch
        _ = git_repo.is_glue_branch
        _ = git_repo.is_sfn_branch
        _ = git_repo.is_airflow_branch

        git_repo.print_git_info(verbose=False)


if __name__ == "__main__":
    from simple_lambda.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.vendor.aws_ops_alpha.git", preview=False)
