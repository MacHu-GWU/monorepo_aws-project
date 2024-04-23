# -*- coding: utf-8 -*-

"""
Manually submit a PDF document to the Textract pipeline.
"""

from pathlib_mate import Path
import aws_textract_pipeline.api as aws_textract_pipeline
from aws_idp_data_store.boto_ses import bsm
from aws_idp_data_store.lbd.textract import workspace

path = Path.dir_here(__file__).joinpath("f1040.pdf")
s3path = workspace.s3dir_landing.joinpath(path.basename)
landing_doc = aws_textract_pipeline.LandingDocument(
    s3uri=s3path.uri,
    doc_type=aws_textract_pipeline.DocTypeEnum.pdf.value,
    features=["FORMS"],
)
landing_doc.dump(bsm=bsm, body=path.read_bytes())
