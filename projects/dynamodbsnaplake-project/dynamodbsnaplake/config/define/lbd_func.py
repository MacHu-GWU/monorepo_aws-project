# -*- coding: utf-8 -*-

"""
Lambda function configurations.
"""

import typing as T
import dataclasses

from boltons.strutils import slugify, under2camel
from ...vendor.import_agent import aws_ops_alpha

from ...constants import LIVE

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
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
        return (
            aws_ops_alpha.aws_lambda_version_and_alias.LATEST
            if self.live_version1 is None
            else self.live_version1
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
            lambda_function.name for lambda_function in self.lambda_functions.values()
        ]

    @property
    def lambda_function_list(self) -> T.List[LambdaFunction]:
        """
        :class:`LambdaFunction` object list.
        """
        return list(self.lambda_functions.values())

    @property
    def lbd_s1_start(self) -> LambdaFunction:
        return self.lambda_functions["s1_start"]

    @property
    def lbd_s2_run_job(self) -> LambdaFunction:
        return self.lambda_functions["s2_run_job"]

    @property
    def lbd_s3_check_status(self) -> LambdaFunction:
        return self.lambda_functions["s3_check_status"]
