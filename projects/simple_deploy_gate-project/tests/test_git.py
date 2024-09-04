# -*- coding: utf-8 -*-

from simple_deploy_gate.git import git_repo


def test():
    _ = git_repo.git_branch_name
    _ = git_repo.semantic_branch_name


if __name__ == "__main__":
    from simple_deploy_gate.tests import run_cov_test

    run_cov_test(__file__, "simple_deploy_gate.git", preview=False)
