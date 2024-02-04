# -*- coding: utf-8 -*-

# --- standard library
import typing as T

# --- third party library (include vendor)
from pathlib import Path
from ..vendor.aws_ecr import (
    get_ecr_repo_uri,
    get_ecr_auth_token,
    docker_login,
    ecr_login as _ecr_login,
    EcrContext,
)

# --- modules from this project
from ..constants import EnvVarNameEnum
from ..env_var import temp_env_var

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager


def ecr_login(bsm_devops: "BotoSesManager"):
    """
    Login to ECR.
    """
    return _ecr_login(bsm_devops)


def build_image(
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    repo_name: str,
    env_name: str,
    parameter_name: str,
    path_dockerfile: Path,
    use_arm: bool = False,
):
    ecr_context = EcrContext.new(
        bsm=bsm_devops,
        repo_name=repo_name,
        path_dockerfile=path_dockerfile,
    )
    additional_args = [
        "--build-arg",
        f"USER_ENV_NAME={env_name}",
        "--build-arg",
        f"PARAMETER_NAME={parameter_name}",
    ]
    if use_arm:
        additional_args.append("--platform=linux/arm64")
    else:
        additional_args.append("--platform=linux/amd64")
    # if IS_CI:
    # this environment variable is from the bootstrap CDK stack declaration
    # role_arn = os.environ["ASSUME_ROLE_FOR_CODEBUILD_CONTAINER"]
    # res = bsm.sts_client.assume_role(
    #     RoleArn=role_arn,
    #     RoleSessionName="codebuild-container-assumed-role",
    #     DurationSeconds=900,
    # )
    # aws_access_key_id = res["Credentials"]["AccessKeyId"]
    # aws_secret_access_key = res["Credentials"]["SecretAccessKey"]
    # aws_session_token = res["Credentials"]["SessionToken"]
    # additional_args.extend(
    #     [
    #         "--build-arg",
    #         f"AWS_REGION={bsm.aws_region}",
    #         "--build-arg",
    #         f"AWS_ACCESS_KEY_ID={aws_access_key_id}",
    #         "--build-arg",
    #         f"AWS_SECRET_ACCESS_KEY={aws_secret_access_key}",
    #         "--build-arg",
    #         f"AWS_SESSION_TOKEN={aws_session_token}",
    #     ]
    # )
    ecr_context.build_image(
        image_tag_list=["latest", pyproject_ops.package_version],
        # Reference: https://docs.docker.com/engine/reference/commandline/build/#build-arg
        additional_args=additional_args,
    )


# @logger.start_and_end(
#     msg="Test Image locally",
#     start_emoji=f"{Emoji.test} {Emoji.package}",
#     error_emoji=f"{Emoji.failed} {Emoji.package}",
#     end_emoji=f"{Emoji.succeeded} {Emoji.package}",
# )
# def test_image(
#     bsm: "BotoSesManager",
#     repo_name: str,
#     env_name: str,
#     check: bool = True,
# ):
#     if check:
#         if (
#             do_we_build_container_image(
#                 is_ci_runtime=IS_CI,
#                 branch_name=GIT_BRANCH_NAME,
#                 is_lambda_branch=IS_LAMBDA_BRANCH,
#                 is_release_branch=IS_RELEASE_BRANCH,
#             )
#             is False
#         ):
#             return
#     with logger.nested():
#         ecr_login(bsm=bsm)
#     ecr_context = EcrContext.new(
#         bsm=bsm,
#         repo_name=repo_name,
#         version=f"{env_name}-{pyproject_ops.package_version}",
#     )
#     ecr_context.test_image()
#
#
# @logger.start_and_end(
#     msg="Push Image to ECR",
#     start_emoji=f"{Emoji.deploy} {Emoji.package}",
#     error_emoji=f"{Emoji.failed} {Emoji.package}",
#     end_emoji=f"{Emoji.succeeded} {Emoji.package}",
# )
# def push_image(
#     bsm: "BotoSesManager",
#     repo_name: str,
#     env_name: str,
#     check: bool = True,
# ):
#     if check:
#         if (
#             do_we_build_container_image(
#                 is_ci_runtime=IS_CI,
#                 branch_name=GIT_BRANCH_NAME,
#                 is_lambda_branch=IS_LAMBDA_BRANCH,
#                 is_release_branch=IS_RELEASE_BRANCH,
#             )
#             is False
#         ):
#             return
#     with logger.nested():
#         ecr_login(bsm=bsm)
#     ecr_context = EcrContext.new(
#         bsm=bsm,
#         repo_name=repo_name,
#         version=pyproject_ops.package_version,
#     )
#     ecr_context.push_image()
