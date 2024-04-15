# -*- coding: utf-8 -*-

from aws_idp_data_store.git import git_repo


def test():
    _ = git_repo.git_branch_name
    _ = git_repo.semantic_branch_name


if __name__ == "__main__":
    from aws_idp_data_store.tests import run_cov_test

    run_cov_test(__file__, "aws_idp_data_store.git", preview=False)
