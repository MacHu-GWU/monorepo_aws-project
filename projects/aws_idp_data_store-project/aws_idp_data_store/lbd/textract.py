# -*- coding: utf-8 -*-

"""
"""

import json
import dataclasses

from s3pathlib import S3Path
import aws_textract_pipeline.api as aws_textract_pipeline
from aws_lambda_event import S3PutEvent, SNSTopicNotificationEvent
from ..vendor.better_dataclasses import DataClass

from ..tracker import Tracker
from ..config.load import config
from ..boto_ses import bsm


@dataclasses.dataclass
class TextractDocumentLocation(DataClass):
    S3Bucket: str = dataclasses.field()
    S3ObjectName: str = dataclasses.field()


@dataclasses.dataclass
class TextractEvent(DataClass):
    JobId: str = dataclasses.field()
    Status: str = dataclasses.field()
    API: str = dataclasses.field()
    JobTag: str = dataclasses.field()
    Timestamp: int = dataclasses.field()
    DocumentLocation: TextractDocumentLocation = TextractDocumentLocation.nested_field()


workspace = aws_textract_pipeline.Workspace(
    s3dir_uri=config.env.s3dir_documents_data_store.uri
)


def lambda_handler(event: dict, context):  # pragma: no cover
    if "Records" in event:
        # s3 event
        if "s3" in event["Records"][0]:
            s3_put_event = S3PutEvent.from_dict(event)
            s3uri = s3_put_event.Records[0].uri
            s3path = S3Path(s3uri)
            if s3uri.startswith(workspace.s3dir_landing.uri):
                tracker = Tracker.new_from_landing_doc(
                    bsm=bsm,
                    landing_doc=aws_textract_pipeline.LandingDocument.load(
                        bsm=bsm,
                        s3path=s3path,
                    ),
                )
                tracker.landing_to_raw(bsm=bsm, workspace=workspace, debug=True)
            elif s3uri.startswith(workspace.s3dir_raw.uri):
                s3path.head_object(bsm=bsm)
                doc_id = s3path.metadata[aws_textract_pipeline.MetadataKeyEnum.doc_id]
                tracker = Tracker.get_one_or_none(task_id=doc_id)
                # raw to component
                tracker.move_to_next_stage(
                    bsm=bsm,
                    workspace=workspace,
                    debug=True,
                )
                # component to textract output
                tracker.move_to_next_stage(
                    bsm=bsm,
                    workspace=workspace,
                    debug=True,
                    sns_topic_arn=config.env.textract_sns_topic_arn,
                    role_arn=config.env.textract_iam_role_arn,
                )
            else:
                pass

        # sns event
        elif "Sns" in event["Records"][0]:
            sns_event = SNSTopicNotificationEvent.from_dict(event)
            textract_event = TextractEvent.from_dict(
                json.loads(sns_event.Records[0].message)
            )
            doc_id = textract_event.JobTag
            tracker = Tracker.get_one_or_none(task_id=doc_id)
            tracker.move_to_next_stage(
                bsm=bsm,
                workspace=workspace,
                debug=True,
                use_form_feature=True,
                sns_topic_arn=config.env.textract_sns_topic_arn,
                role_arn=config.env.textract_iam_role_arn,
            )

    # custom event
    else:
        pass
