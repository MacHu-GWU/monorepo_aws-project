# -*- coding: utf-8 -*-

"""
An automation script to configure an S3 bucket for static website hosting.
"""

import typing as T
import json
from urllib import request

import botocore.exceptions


if T.TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


__version__ = "0.1.1"

checkip_url = "https://checkip.amazonaws.com"


def get_public_ip() -> str:
    """
    Get your public IP address.
    """
    with request.urlopen(checkip_url) as response:
        return response.read().decode("utf-8").strip()


def get_bucket_website(
    s3_client: "S3Client",
    bucket: str,
) -> T.Optional[dict]:
    """
    Get your existing bucket website configuration.

    :return: the website configuration if it exists, otherwise None
    """
    try:
        return s3_client.get_bucket_website(Bucket=bucket)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchWebsiteConfiguration":
            return None
        else:
            raise e


def enable_bucket_static_website_hosting(
    s3_client: "S3Client",
    bucket: str,
    index_document: str = "index.html",
    error_document: T.Optional[str] = None,
) -> dict:
    """
    Reference:

    - Enable static website hosting: https://docs.aws.amazon.com/AmazonS3/latest/userguide/HostingWebsiteOnS3Setup.html#step2-create-bucket-config-as-website
    """
    website_configuration = dict(
        IndexDocument=dict(Suffix="index.html"),
    )
    if error_document is not None:
        website_configuration["ErrorDocument"] = dict(Key=error_document)
    return s3_client.put_bucket_website(
        Bucket=bucket,
        WebsiteConfiguration=dict(
            IndexDocument=dict(Suffix=index_document),
        ),
    )


def turn_off_block_public_access(
    s3_client: "S3Client",
    bucket: str,
):
    """
    You have to turn off "block public access" settings in order to make your
    bucket serving static website.

    Reference:

    - Edit Block Public Access settings: https://docs.aws.amazon.com/AmazonS3/latest/userguide/HostingWebsiteOnS3Setup.html#step3-edit-block-public-access
    """

    return s3_client.put_public_access_block(
        Bucket=bucket,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        },
    )


def get_bucket_policy(
    s3_client: "S3Client",
    bucket: str,
) -> T.Optional[dict]:
    """
    Get your existing bucket policy.

    Reference:

    - Get bucket policy: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_bucket_policy.html

    :return: the bucket policy if it exists, otherwise None
    """
    try:
        res = s3_client.get_bucket_policy(Bucket=bucket)
        return json.loads(res["Policy"])
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucketPolicy":
            return None
        else:
            raise e


def update_policy_statement(
    policy: dict,
    statements: T.List[dict],
) -> dict:
    """
    Update a IAM policy statement in-place. It updates the statement based on the
    statement id.

    Sample policy::

        {
            "Version": "2012-10-17",
            "Statement": [
                ...
            ]
        }

    Sample statements::

        [
            {
                "Sid": ...,
                "Effect": ...,
                "Principal": ...,
                "Action": ...,
                "Resource": ...,
            }
        ]

    Example::

        >>> policy = {
        ...     "Version": "2012-10-17",
        ...     "Statement": [
        ...         {
        ...             "Sid": "s-01",
        ...             ...,
        ...         },
        ...         {
        ...             "Sid": "s-02",
        ...             "Effect": "Allow",
        ...             ...
        ...         },
        ...     ]
        ... }
        >>> statements = [
        ...     {
        ...         "Sid": "s-02",
        ...         "Effect": "Deny",
        ...         ...
        ...     }
        ... ]
        >>> update_policy_statement(policy, statements)
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s-01",
                    ...,
                },
                {
                    "Sid": "s-02",
                    "Effect": "Deny",
                    ...
                },
            ]
        }

    :param policy: the policy to update
    :param statement: the statement to update
    """
    id_iterator = iter([f"AutoStatementId{i}" for i in range(1, 100 + 1)])
    statement_mapper: T.Dict[str, dict] = {
        s.get("Sid", next(id_iterator)): s for s in policy["Statement"]
    }
    for statement in statements:
        if "Sid" not in statement:
            raise ValueError(
                f"Your statement {statement!r} doesn't have an 'Sid' field."
            )
    for statement in statements:
        statement_mapper[statement["Sid"]] = statement
    policy["Statement"] = list(statement_mapper.values())
    return policy


def put_bucket_policy_for_public_website_hosting(
    s3_client: "S3Client",
    bucket: str,
    s3_key_prefix_list: T.Optional[T.List[str]] = None,
):
    """
    Use this function to make your bucket absolutely public readable without
    restriction. This is useful when you want to host a public facing website.

    :param s3_key_prefix_list: ptional list of S3 key prefixes to allow public read access
    """
    if s3_key_prefix_list is None:
        allow_resource = f"arn:aws:s3:::{bucket}/*"
    else:
        allow_resource = [
            f"arn:aws:s3:::{bucket}/{prefix}*" for prefix in s3_key_prefix_list
        ]
    allow_statement = {
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": allow_resource,
    }
    bucket_policy = get_bucket_policy(s3_client, bucket)
    if bucket_policy is None:
        bucket_policy = dict(Version="2012-10-17", Statement=[])
    update_policy_statement(bucket_policy, [allow_statement])
    s3_client.put_bucket_policy(Bucket=bucket, Policy=json.dumps(bucket_policy))


def put_bucket_policy_for_website_hosting(
    s3_client: "S3Client",
    bucket: str,
    s3_key_prefix_list: T.Optional[T.List[str]] = None,
    is_public: bool = False,
    allowed_ip_cidr_block_list: T.Optional[T.List[str]] = None,
    allowed_vpc_endpoint_list: T.Optional[T.List[str]] = None,
    allowed_vpc_ip_cidr_block_list: T.Optional[T.List[str]] = None,
    allowed_aws_account_id_list: T.Optional[T.List[str]] = None,
    allowed_iam_user_id_list: T.Optional[T.List[str]] = None,
    allowed_iam_role_id_list: T.Optional[T.List[str]] = None,
):
    """
    Use this function to make your bucket absolutely public readable with
    some restrictions (e.g. only from a specific IP address or VPC).
    This is useful when you want to host a internal facing website.

    Reference:

    - Add a bucket policy that makes your bucket content publicly available: https://docs.aws.amazon.com/AmazonS3/latest/userguide/HostingWebsiteOnS3Setup.html#step4-add-bucket-policy-make-content-public
    - How can I restrict access to my Amazon S3 bucket using specific VPC endpoints or IP addresses?: https://repost.aws/knowledge-center/block-s3-traffic-vpc-ip

    :param s3_client:
    :param bucket:
    :param s3_key_prefix_list: the s3 key prefix that is allowed
        to access. if not provided, then all s3 objects in the bucket is allowed
    :param is_public: if True, then the bucket will be public.
        either you set is_public to True, either specify all of ``allowed_xyz``
        parameters, you cannot do both
    :param allowed_ip_cidr_block_list:
    :param allowed_vpc_ip_cidr_block_list:
    :param allowed_vpc_endpoint_list:
    :param allowed_aws_account_id_list:
    :param allowed_iam_user_id_list: IAM user id is the ``UserId`` field in the
        boto3.client("sts").get_caller_identity() response
    :param allowed_iam_role_id_list: IAM role id is the ``UserId`` field in the
        boto3.client("sts").get_caller_identity() response
    """
    if is_public is True:
        # all of them has to be None
        if (
            sum(
                [
                    allowed_ip_cidr_block_list is not None,
                    allowed_vpc_ip_cidr_block_list is not None,
                    allowed_vpc_endpoint_list is not None,
                    allowed_aws_account_id_list is not None,
                    allowed_iam_user_id_list is not None,
                    allowed_iam_role_id_list is not None,
                ]
            )
            > 0
        ):
            raise ValueError(
                "you set 'is_public' to True, but you also specified some of the "
                "allowed_xyz parameters, you cannot do both!"
            )
        return put_bucket_policy_for_public_website_hosting(
            s3_client=s3_client,
            bucket=bucket,
            s3_key_prefix_list=s3_key_prefix_list,
        )

    if s3_key_prefix_list is None:
        allow_resource = f"arn:aws:s3:::{bucket}/*"
        deny_resource = [
            f"arn:aws:s3:::{bucket}",
            f"arn:aws:s3:::{bucket}/*",
        ]
    else:
        allow_resource = [
            f"arn:aws:s3:::{bucket}/{prefix}*" for prefix in s3_key_prefix_list
        ]
        deny_resource = [f"arn:aws:s3:::{bucket}"]
        deny_resource.extend(
            [f"arn:aws:s3:::{bucket}/{prefix}*" for prefix in s3_key_prefix_list]
        )

    allow_statement = {
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": allow_resource,
    }

    # TODO: test the logic operator if there's multiple conditions
    condition = {}
    not_ip_address = {}
    string_not_equal = {}
    string_not_like = {}
    if allowed_ip_cidr_block_list is not None:
        not_ip_address["aws:SourceIp"] = allowed_ip_cidr_block_list

    if allowed_vpc_ip_cidr_block_list is not None:
        not_ip_address["aws:VpcSourceIp"] = allowed_vpc_ip_cidr_block_list

    if allowed_vpc_endpoint_list is not None:
        string_not_equal["aws:SourceVpce"] = allowed_vpc_endpoint_list

    user_id_list = []
    if allowed_aws_account_id_list is not None:
        user_id_list.extend(allowed_aws_account_id_list)
    if allowed_iam_user_id_list is not None:
        user_id_list.extend(allowed_iam_user_id_list)
    if allowed_iam_role_id_list is not None:
        user_id_list.extend([f"{role_id}*" for role_id in allowed_iam_role_id_list])
    if user_id_list:
        string_not_like["aws:userId"] = user_id_list

    if not_ip_address:
        condition["NotIpAddress"] = not_ip_address
    if string_not_equal:
        condition["StringNotEquals"] = string_not_equal
    if string_not_like:
        condition["StringNotLike"] = string_not_like

    if condition:
        deny_statement = {
            "Sid": "DenyAllExceptListedBelow",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": deny_resource,
            "Condition": condition,
        }
    else:
        raise ValueError(
            "you set 'is_public' to False, but none of allowed_xyz condition is specified!"
        )

    bucket_policy = get_bucket_policy(s3_client, bucket)
    if bucket_policy is None:
        bucket_policy = dict(Version="2012-10-17", Statement=[])
    update_policy_statement(bucket_policy, [allow_statement, deny_statement])
    s3_client.put_bucket_policy(Bucket=bucket, Policy=json.dumps(bucket_policy))


if __name__ == "__main__":
    from boto_session_manager import BotoSesManager
    from rich import print as rprint

    def print_res(res: dict):
        if "ResponseMetadata" in res:
            del res["ResponseMetadata"]
        rprint(res)

    bsm = BotoSesManager(profile_name="bmt_app_devops_us_east_1")
    bucket = "bmt-app-devops-us-east-1-doc-host"

    s3_client = bsm.s3_client

    website_config = get_bucket_website(s3_client, bucket)
    if website_config is None:
        enable_bucket_static_website_hosting(s3_client, bucket)

    turn_off_block_public_access(s3_client, bucket)

    trusted_ip_address = get_public_ip()

    put_bucket_policy_for_website_hosting(
        s3_client=s3_client,
        bucket=bucket,
        is_public=False,
        allowed_ip_cidr_block_list=[
            f"{trusted_ip_address}/32",
        ],
        allowed_iam_user_id_list=[
            bsm.aws_account_user_id,
        ],
    )
