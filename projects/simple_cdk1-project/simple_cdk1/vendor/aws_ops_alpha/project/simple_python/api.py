# -*- coding: utf-8 -*-

"""
Usage example::

    >>> import aws_ops_alpha.project.simple_lambda.api as simple_lambda_project
"""

from .constants import StepEnum
from .constants import GitBranchNameEnum
from .constants import EnvNameEnum
from .constants import RuntimeNameEnum
from .rule import rule_set
from .step import semantic_branch_rule
from .step import pip_install
from .step import pip_install_dev
from .step import pip_install_test
from .step import pip_install_doc
from .step import pip_install_automation
from .step import pip_install_all
from .step import pip_install_all_in_ci
from .step import poetry_lock
from .step import poetry_export
from .step import run_unit_test
from .step import run_cov_test
from .step import view_cov
from .step import build_doc
from .step import view_doc
from .step import deploy_versioned_doc
from .step import deploy_latest_doc
from .step import view_latest_doc
