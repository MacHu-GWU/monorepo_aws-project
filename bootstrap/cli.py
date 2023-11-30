# -*- coding: utf-8 -*-

"""
CLI interface to run bootstrap steps from CLI.
"""

import fire

from python_lib.steps import c1_teardown_cross_account_permission
from python_lib.steps import c2_teardown_github_action_oidc
from python_lib.steps import s1_setup_venv
from python_lib.steps import s2_cdk_bootstrap
from python_lib.steps import s3_setup_github_action_oidc
from python_lib.steps import s4_setup_cross_account_permission


class Command:
    def c1_teardown_cross_account_permission(self):
        c1_teardown_cross_account_permission.main()

    def c2_teardown_github_action_oidc(self):
        c2_teardown_github_action_oidc.main()

    def s1_setup_venv(self):
        s1_setup_venv.main()

    def s2_cdk_bootstrap(self):
        s2_cdk_bootstrap.main()

    def s3_setup_github_action_oidc(self):
        s3_setup_github_action_oidc.main()

    def s4_setup_cross_account_permission(self):
        s4_setup_cross_account_permission.main()


fire.Fire(Command())
