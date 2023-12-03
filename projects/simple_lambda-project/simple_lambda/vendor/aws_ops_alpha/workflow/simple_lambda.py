# -*- coding: utf-8 -*-

import enum

from ..vendor.semantic_branch import SemanticBranchEnum

from ..constants import AwsOpsSemanticBranchEnum
from ..rule import (
    only_execute_on_certain_branch,
    only_execute_on_certain_runtime,
    only_execute_on_certain_env,
    log_why_not_run_integration_test_in_prod,
    confirm_to_proceed_in_prod,
    only_execute_on_certain_runtime_branch_env,
    log_why_not_create_git_tag_in_non_prod,
    log_why_not_create_git_tag_in_local,
)
from ..runtime import RunTimeEnum


class StepEnum(str, enum.Enum):
    """
    Explains:

    1. Create Python virtual environment.
    2. Install all Python dependencies, reuse cache if possible.
    3. Run code coverage test.
    4. Publish documentation website from the latest code if needed.
    5. Publish Lambda layer version for Python dependencies if needed.
    6. If developer are on an isolated sandbox branch, then deploy Lambda app to it.
    7. If developer are on an isolated sandbox branch, then run integration test on it.
    8. Deploy Lambda app to sandbox.
    9. Run integration test in sandbox.

    If you are not doing a release, this is the end of the pipeline.

    Below are additional steps for release:

    10. Deploy Lambda app to test environment.
    11. Run integration test in test environment.
    12. Deploy Lambda app to prod.
    13. Run integration test in prod, if needed.
    14. Create an immutable config snapshot, so we can roll back anytime.
    15. Create a git tag, so we can roll back anytime.

    This is the end of the pipeline for release.

    If you no longer need this project, you may want to clean up all the deployment.

    16. Delete Lambda app from isolated sandbox branch after your PR is merged.
    17. Delete Lambda app from sandbox.
    18. Delete Lambda app from test environment.
    19. Delete Lambda app from prod.
    """

    # fmt: off
    s01_create_virtualenv = "01 - 🐍 Create Virtualenv"
    s02_install_dependencies = "02 - 💾 Install Dependencies"
    s03_run_code_coverage_test = "03 - 🧪 Run Code Coverage Test"
    s04_public_documentation_website = "04 - 📔 Publish Documentation Website"
    s05_publish_lambda_layer_version_to_devops = "05 - 🏗️ Publish Lambda Layer Version to 🖥️ devops"
    s06_deploy_lambda_app_via_cdk_to_sbx_123 = "06 - 🚀 Deploy Lambda App via CDK to 📦 sbx-123"
    s07_run_integration_test_in_sbx_123 = "07 - 🧪 Run Integration Test in 📦 sbx-123"
    s08_deploy_lambda_app_via_cdk_to_sbx = "08 - 🚀 Deploy Lambda App via CDK to 📦 sbx"
    s09_run_integration_test_in_sbx = "09 - 🧪 Run Integration Test in 📦 sbx"
    s10_deploy_lambda_app_via_cdk_to_tst = "10 - 🚀 Deploy Lambda App via CDK to 🧪 tst"
    s11_run_integration_test_in_test = "11 - 🧪 Run Integration Test in 🧪 tst"
    s12_deploy_lambda_app_via_cdk_to_prd = "12 - 🚀 Deploy Lambda App via CDK to 🏭 prd"
    s13_run_integration_test_in_prd = "13 - 🧪 Run Integration Test in 🏭 prd"
    s14_create_config_snapshot = "🔯 Create Config Snapshot"
    s15_create_git_tag = "15 🏷️ Create Git Tag"
    s16_delete_lambda_app_in_sbx_123 = "16 - 🗑 Delete Lambda App in 📦 sbx-123"
    s17_delete_lambda_app_in_sbx = "17 - 🗑 Delete Lambda App in 📦 sbx"
    s18_delete_lambda_app_in_tst = "18 - 🗑 Delete Lambda App in 🧪 tst"
    s19_delete_lambda_app_in_prd = "19 - 🗑 Delete Lambda App in 🏭 prd"
    # fmt: on


def do_we_run_unit_test(
    is_ci_runtime: bool,
    branch_name: str,
    is_main_branch: bool,
    is_feature_branch: bool,
    is_fix_branch: bool,
    is_layer_branch: bool,
    is_lambda_branch: bool,
    is_release_branch: bool,
) -> bool:
    """
    Check if we should run unit test or coverage test.
    """
    if is_ci_runtime:
        return only_execute_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[
                (is_main_branch, SemanticBranchEnum.main),
                (is_feature_branch, SemanticBranchEnum.feature),
                (is_fix_branch, SemanticBranchEnum.fix),
                (is_layer_branch, AwsOpsSemanticBranchEnum.layer),
                (is_lambda_branch, AwsOpsSemanticBranchEnum.awslambda),
                (is_release_branch, SemanticBranchEnum.release),
            ],
            action=StepEnum.s03_run_code_coverage_test,
            verbose=True,
        )
    # always run unit test on Local
    else:
        return True


def do_we_deploy_doc(
    is_ci_runtime: bool,
    branch_name: str,
    is_doc_branch: bool,
) -> bool:
    """
    This function defines the rule for whether we should deploy the
    documentation website or not.
    """
    # in CI, we only deploy documentation website from doc branch
    if is_ci_runtime:
        return only_execute_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[(is_doc_branch, SemanticBranchEnum.doc)],
            action=StepEnum.s04_public_documentation_website,
            verbose=True,
        )
    # always deploy doc on Local
    else:
        return True


def do_we_deploy_lambda_layer(
    is_ci_runtime: bool,
    branch_name: str,
    is_layer_branch: bool,
) -> bool:
    """
    This function defines the rule for whether we should deploy the
    Lambda layer or not.
    """
    # in CI, we only build layer from layer branch
    if is_ci_runtime:
        return only_execute_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[(is_layer_branch, AwsOpsSemanticBranchEnum.layer)],
            action=StepEnum.s05_publish_lambda_layer_version_to_devops,
            verbose=True,
        )
    # always allow build layer on local
    else:
        return True


def do_we_deploy_app(
    env_name: str,
    prod_env_name: str,
    is_local_runtime: bool,
    branch_name: str,
    is_main_branch: bool,
    is_lambda_branch: bool,
    is_release_branch: bool,
) -> bool:
    """
    This function defines the rule for whether we should deploy the
    Lambda app via CDK or not.
    """
    flag_and_branches = [
        (is_main_branch, SemanticBranchEnum.main),
        (is_lambda_branch, AwsOpsSemanticBranchEnum.awslambda),
        (is_release_branch, SemanticBranchEnum.release),
    ]
    action = "🚀 Deploy Lambda App via CDK"
    flag = only_execute_on_certain_branch(
        branch_name=branch_name,
        flag_and_branches=flag_and_branches,
        action=action,
        verbose=True,
    )
    if env_name == prod_env_name:
        if is_local_runtime:
            return confirm_to_proceed_in_prod(
                prod_env_name=prod_env_name,
                action=action,
                verbose=True,
            )
    return flag


def do_we_run_int_test(
    env_name: str,
    prod_env_name: str,
    is_ci_runtime: bool,
    branch_name: str,
    is_main_branch: bool,
    is_lambda_branch: bool,
    is_release_branch: bool,
) -> bool:
    """
    Check if we should run integration test.

    In CI, we only run integration test when it is a branch that deploy the app.

    There's an exception that, we don't run unit test in prod environment
    because integration test may change the state of the cloud resources,
    and it should be already thoroughly tested in previous environments.
    """
    # never run int test in prod environment
    if env_name == prod_env_name:
        log_why_not_run_integration_test_in_prod(
            env_name=env_name,
            prod_env_name=prod_env_name,
            verbose=True,
        )
        return False

    # in CI, we only run integration test from main / lambda / release branch.
    if is_ci_runtime:
        return only_execute_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[
                (is_main_branch, SemanticBranchEnum.main),
                (is_lambda_branch, AwsOpsSemanticBranchEnum.awslambda),
                (is_release_branch, SemanticBranchEnum.release),
            ],
            action="🧪 Run integration in Non-prd environment",
        )
    # always run int test on Local
    else:
        return True


def do_we_create_config_snapshot(
    is_local_runtime: bool,
    runtime_name: str,
) -> bool:
    """
    This function defines the rule for whether we should create an immutable
    config snapshot in parameter store or S3 backend.
    """
    # we only do this in local runtime
    return only_execute_on_certain_runtime(
        runtime_name=runtime_name,
        flag_and_runtimes=[(is_local_runtime, RunTimeEnum.LOCAL)],
        action=StepEnum.s14_create_config_snapshot,
        verbose=True,
    )


def do_we_create_git_tag(
    env_name: str,
    prod_env_name: str,
    is_ci_runtime: bool,
    branch_name: str,
    is_release_branch: bool,
) -> bool:
    """
    This function defines the rule for whether we should create an immutable
    git Tag after success deployment to prod.

    In CI, we only run unit test when it is a branch that may change the
    application code.
    """
    if is_ci_runtime:
        # we ONLY create git tag after success deployment to prod
        if env_name != prod_env_name:
            log_why_not_create_git_tag_in_non_prod(
                env_name=env_name,
                prod_env_name=prod_env_name,
                verbose=True,
            )
            return False

        return only_execute_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[(is_release_branch, "release")],
            action=StepEnum.s15_create_git_tag,
        )
    # always don't create git tag on local
    else:
        log_why_not_create_git_tag_in_local(
            env_name=env_name,
            prod_env_name=prod_env_name,
            verbose=True,
        )
        return False


def do_we_delete_app(
    env_name: str,
    prod_env_name: str,
    is_local_runtime: bool,
    branch_name: str,
    is_cleanup_branch: bool,
) -> bool:
    """
    Check if we should delete app.
    """
    flag_and_branches = [
        (is_cleanup_branch, "cleanup"),
    ]
    action = "🗑 Delete Lambda App"
    flag = only_execute_on_certain_branch(
        branch_name=branch_name,
        flag_and_branches=flag_and_branches,
        action=action,
        verbose=True,
    )
    if env_name == prod_env_name:
        if is_local_runtime:
            return confirm_to_proceed_in_prod(
                prod_env_name=prod_env_name,
                action=action,
                verbose=True,
            )
    return flag
