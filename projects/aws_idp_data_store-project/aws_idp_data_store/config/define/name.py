# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as aws_arns

from ...boto_ses import bsm

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import Env


@dataclasses.dataclass
class NameMixin:
    @property
    def status_tracking_dynamodb_table_name(self: "Env") -> str:
        return f"{self.project_name_snake}-tracker"

    @property
    def textract_sns_topic_name(self: "Env") -> str:
        return f"{self.project_name_snake}-textract"

    @property
    def textract_sns_topic_arn(self: "Env") -> str:
        return aws_arns.res.SnsTopic.new(
            aws_account_id=bsm.aws_account_id,
            aws_region=bsm.aws_region,
            topic_name=self.textract_sns_topic_name,
        ).to_arn()

    @property
    def textract_iam_role_name(self: "Env") -> str:
        return f"{self.prefix_name_snake}-{bsm.aws_region}-textract"

    @property
    def textract_iam_role_arn(self: "Env") -> str:
        return aws_arns.res.IamRole.new(
            aws_account_id=bsm.aws_account_id,
            name=self.textract_iam_role_name,
        ).to_arn()
