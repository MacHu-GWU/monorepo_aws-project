# -*- coding: utf-8 -*-

import enum

DEVOPS = "devops"
SBX = "sbx"
TST = "tst"
PRD = "prd"


class AwsOpsSemanticBranchEnum(str, enum.Enum):
    lbd = "new"
    awslambda = "lambda"
    layer = "layer"
    ecr = "ecr"
    ami = "ami"
    glue = "glue"
    batch = "batch"
    apigateway = "apigateway"
    sfn = "sfn"
    airflow = "airflow"
