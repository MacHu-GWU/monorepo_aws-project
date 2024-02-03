# -*- coding: utf-8 -*-

from simple_lbd_container.git import git_repo


def test():
    _ = git_repo.git_branch_name
    _ = git_repo.semantic_branch_name


if __name__ == "__main__":
    from simple_lbd_container.tests import run_cov_test

    run_cov_test(__file__, "simple_lbd_container.git", preview=False)
