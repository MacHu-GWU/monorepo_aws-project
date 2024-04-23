# -*- coding: utf-8 -*-

from pathlib_mate import Path
from aws_idp_data_store.tracker import Tracker
from aws_idp_data_store.boto_ses import bsm
from aws_idp_data_store.lbd.textract import workspace

path = Path.dir_here(__file__).joinpath("f1040.pdf")
s3path = workspace.s3dir_landing.joinpath(path.basename)
print(s3path)
# s3path.write_bytes(path.read_bytes(), bsm=bsm)
