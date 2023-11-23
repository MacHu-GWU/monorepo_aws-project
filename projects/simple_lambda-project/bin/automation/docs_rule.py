# -*- coding: utf-8 -*-

from .rule_lib import only_do_on_certain_branch


def do_we_deploy_doc(
    is_ci_runtime: bool,
    branch_name: str,
    is_doc_branch: bool,
) -> bool:
    """
    Check if we should run unit test or coverage test.
    """
    if is_ci_runtime:
        return only_do_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[(is_doc_branch, "doc")],
            action="deploy doc",
            runtime_name="CI",
        )
    else:  # always deploy doc on Local
        return True
