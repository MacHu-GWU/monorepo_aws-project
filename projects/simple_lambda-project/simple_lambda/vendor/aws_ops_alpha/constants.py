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

    :param USER_ENV_NAME: store the current environment name, e.g.
        "devops", "sbx", "tst", "stg", "prd", etc. this environment variable
        has higher priority than the "ENV_NAME"
    :param USER_RUNTIME_NAME: store the name of the current runtime,
        usually you should not use this environment variable directly, instead
        let the ``runtime`` module to detect that automatically. This var
        is useful when you want to override the runtime name for testing.
    :param USER_GIT_BRANCH_NAME: store the name of the current git branch,
        usually you should not use this environment variable directly, instead
        let the ``git`` module to detect that automatically. This var
        is useful when you want to override the git branch name for testing.
    :param USER_GIT_COMMIT_ID: store the name of the current git commit id,
        usually you should not use this environment variable directly, instead
        let the ``git`` module to detect that automatically. This var
        is useful when you want to override the git branch name for testing.
    :param USER_GIT_COMMIT_MESSAGE: store the name of the current git commit message,
        usually you should not use this environment variable directly, instead
        let the ``git`` module to detect that automatically. This var
        is useful when you want to override the git branch name for testing.
    :param ENV_NAME: store the current environment name. if the USER_ENV_NAME is set,
        use USER_ENV_NAME, otherwise, use this one.
    :param PROJECT_NAME: store the name of the current project,
        the project name is part of the AWS resource naming convention
    :param PARAMETER_NAME: store the name of AWS parameter for the configuration
        this environment variable is used in application runtime to get the
        configuration data from AWS parameter store
    """

    USER_ENV_NAME = "USER_ENV_NAME"
    USER_RUNTIME_NAME = "USER_RUNTIME_NAME"
    USER_GIT_BRANCH_NAME = "USER_GIT_BRANCH_NAME"
    USER_GIT_COMMIT_ID = "USER_GIT_COMMIT_ID"
    USER_GIT_COMMIT_MESSAGE = "USER_GIT_COMMIT_MESSAGE"
    ENV_NAME = "ENV_NAME"
    PROJECT_NAME = "PROJECT_NAME"
    PARAMETER_NAME = "PARAMETER_NAME"


class AwsTagNameEnum(BetterStrEnum):
    """
    Common AWS resource tag name enumeration.

    :param tech_project_name: project name for tech
    :param tech_env_name: sbx, prd, etc ...
    :param tech_version: software semantic version, 0.1.2
    :param tech_description: short description
    :param tech_human_creator: usually a name or email
    :param tech_machine_creator: usually a machine identifier
    :param auto_active_time: cron expression that to keep the resource active
    :param auto_delete_at: datetime that to delete the resource
    :param bus_ou: business organization unit
    :param bus_team: the team in your business organization
    :param bus_project_name: project name for business
    :param bus_owner: the owner of the resource, usually an email
    :param bus_user: who is using the resource, usually an email or a team name
    :param sec_confidentiality: confidential level, public, secret, etc ...
    :param sec_compliance: HIPAA, PCI, etc ...
    """

    # fmt: off
    tech_project_name = "tech:project_name"
    tech_env_name = "tech:env_name"
    tech_version = "tech:version"
    tech_description = "tech:description"
    tech_human_creator = "tech:human_creator"
    tech_machine_creator = "tech:machine_creator"
    auto_active_time = "auto:active_time"
    auto_delete_at = "auto:delete_at"
    bus_ou = "bus:ou"
    bus_team = "bus:team"
    bus_project_name = "bus:project_name"
    bus_owner = "bus:owner"
    bus_user = "bus:user"
    sec_confidentiality = "sec:confidentiality"
    sec_compliance = "sec:compliance"
    # fmt: on


class AwsOpsSemanticBranchEnum(BetterStrEnum):
    """
    Common Semantic branch name enumeration.

    :param app: for arbitrary application deployment and integration test
    :param lbd: AWS Lambda stuff
    :param awslambda: AWS Lambda stuff
    :param layer: AWS Lambda layer stuff
    :param ecr: AWS Elastic Container Registry stuff, build and push container image
    :param ami: Amazon Machine Image stuff, build and push VM image
    :param glue: AWS Glue job
    :param batch: AWS Batch
    :param apigateway: AWS API Gateway
    :param ecs: AWS Elastic Container Service, container application stuff
    :param sfn: AWS StepFunction stuff
    :param airflow: AWS managed airflow
    """

    app = "app"  # for arbitrary application deployment and integration test
    lbd = "lbd"  # AWS Lambda stuff
    awslambda = "lambda"  # AWS Lambda stuff
    layer = "layer"  # AWS Lambda layer stuff
    ecr = "ecr"  # AWS Elastic Container Registry stuff, build and push container image
    ami = "ami"  # Amazon Machine Image stuff, build and push VM image
    glue = "glue"  # AWS Glue job
    batch = "batch"  # AWS Batch
    apigateway = "apigateway"  # AWS API Gateway
    ecs = "ecs"  # AWS Elastic Container Service, container application stuff
    sfn = "sfn"  # AWS StepFunction stuff
    airflow = "airflow"  # AWS managed airflow
