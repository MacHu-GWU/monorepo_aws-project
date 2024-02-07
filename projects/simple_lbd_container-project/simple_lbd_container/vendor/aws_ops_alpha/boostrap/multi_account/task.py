# -*- coding: utf-8 -*-

"""
Bootstrap for Multi Workload AWS Accounts Setup.
"""

# --- standard library
import typing as T
import json
import subprocess
import dataclasses

# --- third party library (include vendor)
from s3pathlib import S3Path
import aws_cloudformation.api as aws_cf
import cross_aws_account_iam_role.api as cross_aws_account_iam_role
from ...vendor.aws_s3_static_website_hosting import (
    get_public_ip,
    get_bucket_website,
    enable_bucket_static_website_hosting,
    turn_off_block_public_access,
    put_bucket_policy_for_website_hosting,
)

# --- modules from this project

# --- modules from this submodule

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


def cdk_bootstrap_one_aws_account(bsm: "BotoSesManager"):
    with bsm.awscli():
        args = [
            "cdk",
            "bootstrap",
            f"aws://{bsm.aws_account_id}/{bsm.aws_region}",
        ]
        subprocess.run(args, check=True)


def remove_cdk_bootstrap_stack(bsm: "BotoSesManager"):
    aws_cf.remove_stack(bsm=bsm, stack_name="CDKToolkit")


def setup_cdk_bootstrap(
    bsm_devops: "BotoSesManager",
    workload_bsm_list: T.List["BotoSesManager"],
):  # pragma: no cover
    """
    Run `cdk bootstrap` in the devops and all workload AWS accounts.
    """
    for bsm in [bsm_devops, *workload_bsm_list]:
        cdk_bootstrap_one_aws_account(bsm=bsm)


def teardown_cdk_bootstrap(
    bsm_devops: "BotoSesManager",
    workload_bsm_list: T.List["BotoSesManager"],
):  # pragma: no cover
    """
    Delete the resources created `cdk bootstrap` in the devops and
    all workload AWS accounts.
    """
    for bsm in [bsm_devops, *workload_bsm_list]:
        remove_cdk_bootstrap_stack(bsm=bsm)


@dataclasses.dataclass
class WorkloadAccountIamPermissionSetup:
    """
    Per workload account IAM permission setup.

    :param bsm: the workload account boto session manager, it is used to
        create the CloudFormation stack that includes IAM role and the IAM policy.
    :param stack_name: the CloudFormation stack name.
    :param role_name: the IAM role name.
    :param policy_name: the IAM policy name.
    :param policy_document: the IAM policy document.
    """

    bsm: "BotoSesManager" = dataclasses.field()
    stack_name: str = dataclasses.field()
    role_name: str = dataclasses.field()
    policy_name: str = dataclasses.field()
    policy_document: dict = dataclasses.field()


# fmt: off
def create_grantee_and_owners(
    bsm_devops: "BotoSesManager",
    devops_stack_name: str,
    devops_role_name: str,
    devops_policy_name: str,
    workload_account_iam_permission_setup_list: T.List[WorkloadAccountIamPermissionSetup],
) -> T.Tuple[cross_aws_account_iam_role.Grantee, T.List[cross_aws_account_iam_role.Owner]]: # pragma: no cover
# fmt: on
    iam_arn = cross_aws_account_iam_role.IamRoleArn(
        account=bsm_devops.aws_account_id,
        name=devops_role_name,
    )
    grantee = cross_aws_account_iam_role.Grantee(
        bsm=bsm_devops,
        stack_name=devops_stack_name,
        iam_arn=iam_arn,
        policy_name=devops_policy_name,
    )
    owner_list = list()
    for setup in workload_account_iam_permission_setup_list:
        owner = cross_aws_account_iam_role.Owner(
            bsm=setup.bsm,
            stack_name=setup.stack_name,
            role_name=setup.role_name,
            policy_name=setup.policy_name,
            policy_document=setup.policy_document,
        )
        owner.grant(grantee)
        owner_list.append(owner)
    return grantee, owner_list


# fmt: off
def setup_cross_account_iam_permission(
    bsm_devops: "BotoSesManager",
    devops_stack_name: str,
    devops_role_name: str,
    devops_policy_name: str,
    workload_account_iam_permission_setup_list: T.List[WorkloadAccountIamPermissionSetup],
): # pragma: no cover
    """
    Create IAM role in workload accounts and grant the devops account IAM role
    permission to assume the workload account IAM role.

    :param bsm_devops: the devops account boto session manager.
    :param devops_stack_name: the devops account CloudFormation stack name.
    :param devops_role_name: the devops account IAM role name that performs
        CI/CD tasks, it should be able to assume the workload account IAM role.
    :param devops_policy_name: the devops account IAM policy name that defines
        the permission to assume the workload account IAM role.
    :param workload_account_iam_permission_setup_list: list of
        :class`WorkloadAccountIamPermissionSetup` objects.
    """
# fmt: on
    grantee, owner_list = create_grantee_and_owners(
        bsm_devops=bsm_devops,
        devops_stack_name=devops_stack_name,
        devops_role_name=devops_role_name,
        devops_policy_name=devops_policy_name,
        workload_account_iam_permission_setup_list=workload_account_iam_permission_setup_list,
    )

    cross_aws_account_iam_role.deploy(
        grantee_list=[grantee],
        owner_list=owner_list,
    )


# fmt: off
def teardown_cross_account_iam_permission(
    bsm_devops: "BotoSesManager",
    devops_stack_name: str,
    devops_role_name: str,
    devops_policy_name: str,
    workload_account_iam_permission_setup_list: T.List[WorkloadAccountIamPermissionSetup],
): # pragma: no cover
    """
    Delete the resources created by `setup_cross_account_iam_permission`.
    """
# fmt: on
    grantee, owner_list = create_grantee_and_owners(
        bsm_devops=bsm_devops,
        devops_stack_name=devops_stack_name,
        devops_role_name=devops_role_name,
        devops_policy_name=devops_policy_name,
        workload_account_iam_permission_setup_list=workload_account_iam_permission_setup_list,
    )
    cross_aws_account_iam_role.delete(
        grantee_list=[grantee],
        owner_list=owner_list,
    )


def setup_devops_account_s3_bucket(
    bsm_devops: "BotoSesManager",
    artifacts_s3_bucket: str,
    docs_s3_bucket: str,
    workload_account_iam_permission_setup_list: T.List[WorkloadAccountIamPermissionSetup],
    artifacts_s3_prefix: str = "",
    docs_s3_prefix: str = "",
    white_list_your_ip: bool = False,
): # pragma: no cover
    """
    Typically we need two S3 buckets in the devops account.

    1. artifacts bucket: used to store artifacts from CI/CD pipeline
    2. docs bucket: used to store static website for documentation

    This function creates the two buckets, grant the workload account IAM role
    permission to access the artifacts bucket, and configure the docs bucket
    for static website hosting.

    :param bsm_devops: the devops account boto session manager.
    :param artifacts_s3_bucket: the artifacts bucket name.
    :param docs_s3_bucket: the docs bucket name.
    :param workload_account_iam_permission_setup_list: list of
        :class`WorkloadAccountIamPermissionSetup` objects.
    :param artifacts_s3_prefix: optional S3 prefix for the artifacts bucket.
    :param docs_s3_prefix: optional S3 prefix for the docs bucket.
    :param white_list_your_ip: whether to white list your IP address to access
        the docs bucket.
    """
    # create s3 bucket to store artifacts
    s3bucket_artifacts = S3Path(artifacts_s3_bucket)
    if s3bucket_artifacts.exists(bsm=bsm_devops) is False:
        s3bucket_artifacts.create_bucket(region=bsm_devops.aws_region)

    # setup artifacts bucket policy to allow workload account to read artifacts
    s3dir_artifacts = s3bucket_artifacts.joinpath(artifacts_s3_prefix).to_dir()
    devops_artifacts_bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "allow IAM role on workload accounts to access this s3 bucket",
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        f"arn:aws:iam::{setup.bsm.aws_account_id}:root"
                        for setup in workload_account_iam_permission_setup_list
                    ],
                },
                "Action": [
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:GetObjectTagging",
                    "s3:GetObjectAttributes",
                ],
                "Resource": [
                    f"arn:aws:s3:::{artifacts_s3_bucket}",
                    f"arn:aws:s3:::{artifacts_s3_bucket}/{s3dir_artifacts.key}*",
                ],
            }
        ],
    }

    bsm_devops.s3_client.put_bucket_policy(
        Bucket=artifacts_s3_bucket,
        Policy=json.dumps(devops_artifacts_bucket_policy),
    )

    # create s3 bucket to store documentation
    s3bucket_docs = S3Path(docs_s3_bucket)
    if s3bucket_docs.exists(bsm=bsm_devops) is False:
        s3bucket_docs.create_bucket(region=bsm_devops.aws_region)

    # enable static website hosting for documentation bucket
    website_config = get_bucket_website(bsm_devops.s3_client, docs_s3_bucket)
    if website_config is None:
        enable_bucket_static_website_hosting(bsm_devops.s3_client, docs_s3_bucket)

    turn_off_block_public_access(bsm_devops.s3_client, docs_s3_bucket)

    allowed_aws_account_id_list = [
        bsm_devops.aws_account_id,
    ]
    for setup in workload_account_iam_permission_setup_list:
        allowed_aws_account_id_list.append(setup.bsm.aws_account_id)

    kwargs = dict(
        s3_client=bsm_devops.s3_client,
        bucket=docs_s3_bucket,
        is_public=False,
        # by default, give access to devops and workload accounts.
        allowed_aws_account_id_list=allowed_aws_account_id_list,
    )

    # always give the devops boto session access to the docs bucket
    if ":user/" in bsm_devops.principal_arn:
        kwargs["allowed_iam_user_id_list"] = [
            bsm_devops.aws_account_user_id,
        ]

    if ":assumed-role/" in bsm_devops.principal_arn:
        kwargs["allowed_iam_role_id_list"] = [
            bsm_devops.aws_account_user_id,
        ]

    if docs_s3_prefix:
        kwargs["s3_key_prefix_list"] = [docs_s3_prefix]

    # if white_list_your_ip is True, then we will white list your IP address
    if white_list_your_ip is True:
        kwargs["allowed_ip_cidr_block_list"] = [
            f"{get_public_ip()}/32",
        ]

    put_bucket_policy_for_website_hosting(**kwargs)


def teardown_devops_account_s3_bucket(
    bsm_devops: "BotoSesManager",
    artifacts_s3_bucket: str,
    docs_s3_bucket: str,
    workload_account_iam_permission_setup_list: T.List[WorkloadAccountIamPermissionSetup],
): # pragma: no cover
    """
    Typically we should NOT delete the artifacts and document S3 buckets in devops account.
    """
    pass
