# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``step.py`` module should have visualized logging.
"""

# --- standard library
import typing as T
import json
from pathlib import Path

# --- third party library (include vendor)
import botocore.exceptions
import tt4human.api as tt4human
from ...vendor.emoji import Emoji

# --- modules from this project
from ...logger import logger
from ...aws_helpers.api import aws_ecr_helpers
from ...rule_set import should_we_do_it

# --- modules from this submodule
from .simple_lbd_container_truth_table import StepEnum, truth_table

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager


@logger.start_and_end(
    msg="Create ECR Repository",
    start_emoji=f"{Emoji.build} {Emoji.container}",
    error_emoji=f"{Emoji.failed} {Emoji.container}",
    end_emoji=f"{Emoji.succeeded} {Emoji.container}",
    pipe=Emoji.container,
)
def create_ecr_repository(
    bsm_devops: "BotoSesManager",
    workload_bsm_list: T.List["BotoSesManager"],
    repo_name: str,
    image_tag_mutability: str = "MUTABLE",
    expire_untagged_after_days: int = 30,
    tags: T.Optional[T.Dict[str, str]] = None,
):  # pragma: no cover
    """
    Create ECR repository and put life cycle policy.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/describe_repositories.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/create_repository.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/put_lifecycle_policy.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/set_repository_policy.html
    """
    try:
        bsm_devops.ecr_client.describe_repositories(repositoryNames=[repo_name])
        logger.info("ECR repository already exists.")
    except botocore.exceptions.ClientError as e:
        logger.info("ECR repository doesn't exists, create it.")
        if e.response["Error"]["Code"] == "RepositoryNotFoundException":
            kwargs = dict(
                repositoryName=repo_name,
                imageTagMutability=image_tag_mutability,
            )
            if tags:
                kwargs["tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]
            bsm_devops.ecr_client.create_repository(**kwargs)
        else:  # pragma: no cover
            raise e

    logger.info("Put life cycle policy.")
    life_cycle_policy = {
        "rules": [
            {
                "rulePriority": 1,
                "description": "string",
                "selection": {
                    "tagStatus": "untagged",
                    "countType": "sinceImagePushed",
                    "countUnit": "days",
                    "countNumber": expire_untagged_after_days,
                },
                "action": {"type": "expire"},
            }
        ]
    }
    res = bsm_devops.ecr_client.put_lifecycle_policy(
        repositoryName=repo_name,
        lifecyclePolicyText=json.dumps(life_cycle_policy),
    )

    if tags:
        logger.info(f"put tags to ECR repository.")
        res = bsm_devops.ecr_client.tag_resource(
            resourceArn=f"arn:aws:ecr:{bsm_devops.aws_region}:{bsm_devops.aws_account_id}:repository/{repo_name}",
            tags=[{"Key": k, "Value": v} for k, v in tags.items()],
        )

    logger.info("Set repository policy for cross account access.")
    # Ref:
    # - https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-policy-examples.html
    # - https://repost.aws/knowledge-center/lambda-ecr-image
    repository_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowCrossAccountGet",
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        f"arn:aws:iam::{bsm.aws_account_id}:root"
                        for bsm in workload_bsm_list
                    ]
                },
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer",
                ],
            },
            {
                "Sid": "LambdaECRImageCrossAccountRetrievalPolicy",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com",
                },
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer",
                ],
                "Condition": {
                    "StringLike": {
                        "aws:sourceARN": [
                            f"arn:aws:lambda:us-east-1:{bsm.aws_account_id}:function:*"
                            for bsm in workload_bsm_list
                        ]
                    }
                },
            },
        ],
    }
    res = bsm_devops.ecr_client.set_repository_policy(
        repositoryName=repo_name,
        policyText=json.dumps(repository_policy),
    )
    res = bsm_devops.ecr_client.get_repository_policy(
        repositoryName=repo_name,
    )


@logger.start_and_end(
    msg="Build Lambda Container Image Locally",
    start_emoji=f"{Emoji.build} {Emoji.awslambda} {Emoji.package}",
    error_emoji=f"{Emoji.failed} {Emoji.awslambda} {Emoji.package}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda} {Emoji.package}",
    pipe=Emoji.awslambda,
)
def build_lambda_container(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    repo_name: str,
    path_dockerfile: Path,
    use_arm: bool = False,
    check=True,
    step: str = StepEnum.build_lambda_container.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return
    aws_ecr_helpers.build_image(
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        repo_name=repo_name,
        path_dockerfile=path_dockerfile,
        use_arm=use_arm,
    )


@logger.start_and_end(
    msg="Push Lambda Container Image to ECR",
    start_emoji=f"{Emoji.build} {Emoji.awslambda} {Emoji.package}",
    error_emoji=f"{Emoji.failed} {Emoji.awslambda} {Emoji.package}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda} {Emoji.package}",
    pipe=Emoji.awslambda,
)
def push_lambda_container(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    repo_name: str,
    path_dockerfile: Path,
    check=True,
    step: str = StepEnum.build_lambda_container.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return
    aws_ecr_helpers.push_image(
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        repo_name=repo_name,
        path_dockerfile=path_dockerfile,
    )
