# -*- coding: utf-8 -*-

"""
AWS Step Functions Context Management Module

This module provides utilities and classes for managing AWS Step Functions execution context,
including serialization, deserialization, and S3 storage operations. It aims to simplify
the process of storing and retrieving arbitrary data for AWS Step Function executions,
avoiding the complexity of AWS Step Function's built-in inter-state input/output mechanism.

Usage:

This module allows passing only the execution ID as input to each Lambda function
using the ``"Payload": {"exec_arn.$": "$$.Execution.Id"}`` syntax,
while storing and retrieving the full context data from S3. This approach provides
better control and flexibility in managing context and input/ouput data across multiple steps.

Classes:

- :class:`SfnCtx`: Represents the context of an AWS Step Functions execution.
"""

import typing as T
import json
import base64
import dataclasses

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client


def split_uri(uri: str) -> T.Tuple[str, str]:
    """
    Splits an S3 URI into bucket and key parts.
    """
    parts = uri.split("/", 3)
    bucket, key = parts[2], parts[3]
    return bucket, key


def b64encode(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")


def b64decode(s: str) -> str:
    return base64.b64decode(s.encode("utf-8")).decode("utf-8")


@dataclasses.dataclass
class SfnCtx:
    """
    Represents the context of an AWS Step Functions execution.

    This class encapsulates the execution ARN and associated data,
    providing methods to serialize the context to S3 and deserialize it back.
    It serves as a utility to store arbitrary data for an AWS Step Function execution,
    avoiding the need to use AWS Step Function's built-in complex inter-state
    input/output mechanism.

    :param exec_arn: The ARN (Amazon Resource Name) of the Step Functions execution.
    :param data: A dictionary containing the context data of the execution.

    **Methods**

    - :meth:`write`: Serializes and writes the context to an S3 location.
    - :meth:`read`: Class method to read and deserialize a context from an S3 location.

    **Example**

    >>> ctx = SfnCtx(exec_arn="arn:aws:states:...:execution:...", data={"key": "value"})
    >>> s3_uri = ctx.write(s3_client, "s3://my-bucket/my_state_machine_name/")
    >>> retrieved_ctx = SfnCtx.read(s3_client, "s3://my-bucket/contexts/", "arn:aws:states:...:execution:...")
    >>> retrieved_ctx.data
    {'key': 'value'}

    .. seealso::

        https://docs.aws.amazon.com/step-functions/latest/dg/input-output-contextobject.html
    """

    exec_arn: str = dataclasses.field()
    data: dict = dataclasses.field()

    def write(
        self,
        s3_client: "S3Client",
        s3dir_uri: str,
    ) -> str:
        """
        Writes the context data to a specified S3 location.

        :param s3_client: An initialized boto3 S3 client.
        :param s3dir_uri: The S3 URI of the directory to write to.

        :return: The full S3 URI of the written context file.
        """
        bucket, key = split_uri(s3dir_uri)
        if key.endswith("/") is False:
            key += "/"
        key = key + f"{b64encode(self.exec_arn)}.json"
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(self.data, ensure_ascii=False),
            ContentType="application/json",
        )
        uri = f"s3://{bucket}/{key}"
        return uri

    @classmethod
    def read(
        cls,
        s3_client: "S3Client",
        s3dir_uri: str,
        exec_arn: str,
    ):
        """
        Reads and deserializes a context from a specified S3 location.

        :param s3_client: An initialized boto3 S3 client.
        :param s3dir_uri: The S3 URI of the directory to read from.
        :param exec_arn: The execution ARN to identify the correct context file.

        :return: An instance of SfnCtx containing the deserialized context data.
        """
        bucket, key = split_uri(s3dir_uri)
        if key.endswith("/") is False:
            key += "/"
        key = key + f"{b64encode(exec_arn)}.json"
        res = s3_client.get_object(Bucket=bucket, Key=key)
        data = json.loads(res["Body"].read())
        return cls(exec_arn=exec_arn, data=data)
