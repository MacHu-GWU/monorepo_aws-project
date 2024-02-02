# -*- coding: utf-8 -*-

import typing as T

import aws_cdk as cdk
from aws_cdk import (
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_lambda as lambda_,
)

import simple_lambda.vendor.aws_ops_alpha.api as aws_ops_alpha
from ...paths import (
    dir_lambda_deploy,
    path_source_zip,
)
from ...git import git_repo
from ...boto_ses import boto_ses_factory
from ...vendor.hashes import hashes

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import MainStack


USER_ENV_NAME = aws_ops_alpha.EnvVarNameEnum.USER_ENV_NAME.value


class LambdaMixin:
    def mk_rg2_lbd(self: "MainStack"):
        # fmt: off
        source_sha256 = hashes.of_paths([dir_lambda_deploy])
        KEY_FUNC = "func"
        KEY_ALIAS = "alias"
        self.lambda_func_mapper: T.Dict[
            str,
            T.Dict[
                str,
                T.Union[lambda_.Function, lambda_.Alias]
            ]
        ] = dict()
        for lbd_func_config in self.env.lambda_functions.values():
            # create layer declaration from config
            layers = list()
            for ith, layer_arn in enumerate(lbd_func_config.layers, start=1):
                # layer_arn can be either a full arn or a layer version id (1, 2, ...)
                if not layer_arn.startswith("arn:"):  # pragma: no cover
                    final_layer_arn = (
                        f"arn:aws:lambda:{boto_ses_factory.bsm_devops.aws_region}:{boto_ses_factory.bsm_devops.aws_account_id}:layer"
                        f":{self.env.lambda_layer_name}:{layer_arn}"
                    )
                else:
                    final_layer_arn = layer_arn
                layer = lambda_.LayerVersion.from_layer_version_arn(
                    self,
                    f"LambdaLayer{lbd_func_config.short_name_camel}{ith}",
                    layer_version_arn=final_layer_arn,
                )
                layers.append(layer)

            # declare lambda function
            env_vars = self.env.env_vars
            env_vars.update(
                {
                    USER_ENV_NAME: self.env.env_name,
                    "SOURCE_SHA256": source_sha256,
                    "GIT_COMMIT_ID": git_repo.git_commit_id,
                    "CONFIG_VERSION": self.config.version,
                }
            )
            kwargs = dict(
                function_name=lbd_func_config.name,
                code=lambda_.Code.from_asset(f"{path_source_zip}"),
                handler=f"lambda_function.{lbd_func_config.handler}",
                runtime=lambda_.Runtime.PYTHON_3_9,
                memory_size=lbd_func_config.memory,
                timeout=cdk.Duration.seconds(lbd_func_config.timeout),
                layers=layers,
                environment=env_vars,
                current_version_options=lambda_.VersionOptions(
                    removal_policy=cdk.RemovalPolicy.RETAIN,
                    retry_attempts=1,
                ),
            )
            if lbd_func_config.iam_role is None:
                kwargs["role"] = self.iam_role_for_lambda
            # use role managed by external projects
            else:  # pragma: no cover
                kwargs["role"] = iam.Role.from_role_arn(
                    self,
                    f"ImportedLambdaRole{lbd_func_config.short_name_camel}",
                    role_arn=lbd_func_config.iam_role,
                )
            if lbd_func_config.reserved_concurrency is not None:  # pragma: no cover
                kwargs["reserved_concurrent_executions"] = lbd_func_config.reserved_concurrency
            lbd_func = lambda_.Function(
                self,
                f"LambdaFunc{lbd_func_config.short_name_camel}",
                **kwargs,
            )

            # declare lambda function alias
            kwargs = dict(
                alias_name="LIVE",
            )
            if lbd_func_config.live_version1 is None:
                kwargs["version"] = lbd_func.current_version
            else:
                kwargs["version"] = lambda_.Version.from_version_arn(
                    self,
                    f"LambdaVersion1ForLive{lbd_func_config.short_name_camel}",
                    version_arn=f"{lbd_func.function_arn}:{lbd_func_config.target_live_version1}",
                )

            # handle optional canary deployment
            if lbd_func_config.live_version2 is not None:  # pragma: no cover
                if not (0.01 <= lbd_func_config.live_version2_percentage <= 0.99):
                    raise ValueError(
                        "version2 percentage has to be between 0.01 and 0.99."
                    )
                if lbd_func_config.target_live_version1 == "$LATEST":
                    raise ValueError(
                        "$LATEST is not supported for an alias pointing to more than 1 version."
                    )
                kwargs["additional_versions"] = [
                    lambda_.VersionWeight(
                        version=lambda_.Version.from_version_arn(
                            self,
                            f"LambdaVersion2ForLive{lbd_func_config.short_name_camel}",
                            version_arn=f"{lbd_func.function_arn}:{lbd_func_config.live_version2}",
                        ),
                        weight=lbd_func_config.live_version2_percentage,
                    )
                ]
            lbd_func_alias = lambda_.Alias(
                self,
                f"LambdaAlias{lbd_func_config.short_name_camel}",
                **kwargs,
            )
            lbd_func_alias.node.add_dependency(lbd_func)

            # put lambda function and alias into mapper, so we can access them later
            self.lambda_func_mapper[lbd_func_config.name] = {
                KEY_FUNC: lbd_func,
                KEY_ALIAS: lbd_func_alias,
            }

        # ----------------------------------------------------------------------
        # Configure S3 Notification
        #
        # note:
        # based on this issue: https://github.com/aws/aws-cdk/issues/23940
        # it is impossible to use S3Bucket that is not defined in this stack
        # for ``aws_cdk.aws_lambda_event_sources.S3EventSource``
        # this is the only choice for now
        # ----------------------------------------------------------------------
        bucket = s3.Bucket.from_bucket_attributes(
            self,
            "ImportedBucket",
            bucket_arn=f"arn:aws:s3:::{self.env.s3dir_source.bucket}",
        )

        # --- use latest version
        # bucket.add_event_notification(
        #     s3.EventType.OBJECT_CREATED,
        #     s3_notifications.LambdaDestination(
        #         self.lambda_func_mapper[self.env.lbd_s3sync.name][KEY_FUNC],
        #     ),
        #     s3.NotificationKeyFilter(
        #         prefix=f"{self.env.s3dir_source.key}",
        #     ),
        # )
        #
        # --- use lambda alias
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(
                lambda_.Function.from_function_attributes(
                    self,
                    f"LambdaAliasAttribute{self.env.lbd_s3sync.short_name_camel}",
                    function_arn=self.lambda_func_mapper[self.env.lbd_s3sync.name][KEY_ALIAS].function_arn,
                    same_environment=True,
                ),
            ),
            s3.NotificationKeyFilter(
                prefix=f"{self.env.s3dir_source.key}",
            ),
        )

        # add custom resource tags to Lambda Function
        for dct in self.lambda_func_mapper.values():
            lbd_func = dct[KEY_FUNC]
            cdk.Tags.of(lbd_func).add("tech:source_sha256", source_sha256)
        # fmt: on