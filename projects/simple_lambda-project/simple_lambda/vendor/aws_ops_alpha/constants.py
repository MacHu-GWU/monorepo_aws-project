# -*- coding: utf-8 -*-

from .vendor.better_enum import BetterStrEnum


class CommonEnvNameEnum(BetterStrEnum):
    """
    Common environment name enumeration.
    """

    devops = "devops"  # DevOps
    sbx = "sbx"  # Sandbox
    dev = "dev"  # Development
    tst = "tst"  # Test
    stg = "stg"  # Staging
    qa = "qa"  # Quality Assurance
    prd = "prd"  # Production


class EnvVarNameEnum(BetterStrEnum):
    """
    Common environment variable name enumeration.
    """
    # this is an environment variable name that is used to store the current
    # environment name, e.g. "devops", "sbx", "tst", "stg", "prd", etc.
    USER_ENV_NAME = "USER_ENV_NAME"


class AwsOpsSemanticBranchEnum(BetterStrEnum):
    """
    Common Semantic branch name enumeration.
    """

    app = "app" # for arbitrary application deployment and integration test
    lbd = "lbd" # AWS Lambda stuff
    awslambda = "lambda" # AWS Lambda stuff
    layer = "layer" # AWS Lambda layer stuff
    ecr = "ecr" # AWS Elastic Container Registry stuff, build and push container image
    ami = "ami" # Amazon Machine Image stuff, build and push VM image
    glue = "glue" # AWS Glue job
    batch = "batch" # AWS Batch
    apigateway = "apigateway" # AWS API Gateway
    ecs = "ecs" # AWS Elastic Container Service, container application stuff
    sfn = "sfn" # AWS StepFunction stuff
    airflow = "airflow" # AWS managed airflow
