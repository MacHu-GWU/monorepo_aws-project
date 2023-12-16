# -*- coding: utf-8 -*-

"""
Lambda function configurations.
"""

import typing as T
import dataclasses

from boto_session_manager import BotoSesManager
from boltons.strutils import slugify, under2camel

from ...vendor.aws_lambda_version_and_alias import LATEST, publish_version, deploy_alias
from ...constants import LIVE

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import Env


@dataclasses.dataclass
class LambdaFunction:
    """
    Represent a lambda function.
    """

    env: "Env" = dataclasses.field(init=False)
    short_name: T.Optional[str] = dataclasses.field(default=None)
    handler: T.Optional[str] = dataclasses.field(default=None)
    timeout: T.Optional[int] = dataclasses.field(default=None)
    memory: T.Optional[int] = dataclasses.field(default=None)
    iam_role: T.Optional[str] = dataclasses.field(default=None)
    env_vars: T.Optional[T.Dict[str, str]] = dataclasses.field(default=None)
    layers: T.Optional[T.List[str]] = dataclasses.field(default_factory=list)
    subnet_ids: T.Optional[T.List[str]] = dataclasses.field(default=None)
    security_group_ids: T.Optional[T.List[str]] = dataclasses.field(default=None)
    reserved_concurrency: T.Optional[int] = dataclasses.field(default=None)
    live_version1: T.Optional[str] = dataclasses.field(default=None)
    live_version2: T.Optional[str] = dataclasses.field(default=None)
    live_version2_percentage: T.Optional[float] = dataclasses.field(default=None)

    @property
    def name(self) -> str:
        """
        Full name of the Lambda function.
        """
        return f"{self.env.project_name_snake}-{self.env.env_name}-{self.short_name}"

    @property
    def short_name_slug(self) -> str:
        """
        Example: ``my-func``
        """
        return slugify(self.short_name, delim="-")

    @property
    def short_name_snake(self) -> str:
        """
        Example: ``my_func``
        """
        return slugify(self.short_name, delim="_")

    @property
    def short_name_camel(self) -> str:
        """
        The lambda function short name in camel case. This is usually used
        in CloudFormation logic ID.

        Example: ``MyFunc``
        """
        return under2camel(slugify(self.short_name, delim="_"))

    @property
    def target_live_version1(self) -> str:
        """
        Get the lambda version you want to set as ALIAS 'LIVE'.
        If the live version is not specified, use the '$LATEST' version.
        :return:
        """
        return LATEST if self.live_version1 is None else self.live_version1

    def publish_version(
        self,
        bsm: BotoSesManager,
    ) -> T.Tuple[bool, int]:  # pragma: no cover
        """
        Publish a new version. This API is idempotent, i.e. if the $LATEST
        version is already the latest published version, then nothing will happen.

        :return: a tuple of two items, first item is a boolean flag to indicate
            that if a new version is created. the second item is the version id.
        """
        return publish_version(bsm.lambda_client, func_name=self.name)

    def deploy_alias(
        self,
        bsm: BotoSesManager,
    ) -> T.Tuple[bool, T.Optional[str]]:  # pragma: no cover
        """
        Point the alias to the given version or split traffic between two versions.

        :return: a tuple of two items; first item is a boolean flag to indicate
            whether a creation or update is performed; second item is the alias
            revision id, if creation or update is not performed, then return None.
        """
        return deploy_alias(
            bsm,
            func_name=self.name,
            alias=LIVE,
            version1=self.live_version1,
            version2=self.live_version2,
            version2_percentage=self.live_version2_percentage,
        )


@dataclasses.dataclass
class LambdaFunctionMixin:
    lambda_functions: T.Dict[str, LambdaFunction] = dataclasses.field(
        default_factory=dict
    )

    @property
    def lambda_function_name_list(self) -> T.List[str]:
        """
        Example::

            >>> LambdaFunctionMixin().lambda_function_name_list
            [
                '${project_name}-${env_name}-${short_name1}',
                '${project_name}-${env_name}-${short_name2}',
                '${project_name}-${env_name}-${short_name3}',
            ]
        """
        return [
            lambda_function.name
            for lambda_function in self.lambda_functions.values()
        ]

    @property
    def lambda_function_list(self) -> T.List[LambdaFunction]:
        """
        Lambda function object list.
        """
        return list(self.lambda_functions.values())

    @property
    def lbd_hello(self) -> LambdaFunction:
        return self.lambda_functions["hello"]

    @property
    def lbd_s3sync(self) -> LambdaFunction:
        return self.lambda_functions["s3sync"]
