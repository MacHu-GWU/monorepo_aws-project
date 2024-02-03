# -*- coding: utf-8 -*-

"""
This script declares the AWS CDK stack for CI/CD AWS resources.
"""

# ------------------------------------------------------------------------------
# Import dependencies
# ------------------------------------------------------------------------------
import json
import dataclasses
from pathlib_mate import Path

import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets
import aws_cdk.aws_codecommit as codecommit
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_codepipeline as codepipeline
import aws_cdk.aws_codepipeline_actions as codepipeline_actions
from constructs import Construct


# ------------------------------------------------------------------------------
# Config Management
# ------------------------------------------------------------------------------
dir_here = Path(__file__).absolute().parent
dir_bootstrap = dir_here
path_source_zip = dir_bootstrap / "source.zip"
path_build_lambda_source_py = dir_bootstrap / "build_lambda_source.py"
path_du_config_json = dir_bootstrap / "du-config.json"
dir_repo_root = dir_bootstrap.parent.parent.parent
path_repo_config_json = dir_repo_root / "shared" / "repo-config.json"


@dataclasses.dataclass
class DeploymentUnit:
    """
    An abstraction of a deployment unit. A deployment unit is a Python project
    that includes application code, test code, config management,
    infrastructure as code declaration, and DevOps automation script. It can be
    deployed independently without interfering other deployment units. For
    cross deployment unit data sharing, you can use AWS CloudFormation output
    value exports. For cross deployment unit communication, you can use the
    AWS StepFunction to orchestrate the workflow, or you can use the event driven
    integration pattern to connect them together.

    :param repo_name: the git repository name
    :param repo_name_prefix: this is the common prefix for all the AWS resource name
        for this deployment unit, see ``du_name_prefix`` for more information.
    :param du_name: deployment unit name, this is the git branch prefix that
        triggers the CI/CD.
    :param du_folder: this is the sub-folder name of your deployment unit,
        the relative path to git repo root dir should be "projects/${du_folder}/"
        it has to have a buildspec.yml file in it.
    :param du_name_prefix: this is the common prefix for all the AWS resource name
        for this deployment unit the full prefix is actually
        "${repo_name_prefix}-${du_name_prefix}" where the ${repo_name_prefix}
        is defined in the "shared/repo-config.json" file
    """
    repo_name: str = dataclasses.field()
    repo_name_prefix: str = dataclasses.field()
    du_name: str = dataclasses.field()
    du_folder: str = dataclasses.field()
    du_name_prefix: str = dataclasses.field()

    @property
    def name_prefix_slug(self) -> str:
        return f"{self.repo_name_prefix}-{self.du_name_prefix}".replace("_", "-")

    @property
    def name_prefix_snake(self) -> str:
        return f"{self.repo_name_prefix}-{self.du_name_prefix}".replace("-", "_")

    @property
    def lambda_iam_role_name(self) -> str:
        return f"{self.name_prefix_snake}-codebuild_trigger_lambda_role"

    @property
    def lambda_function_name(self) -> str:
        return f"{self.name_prefix_snake}-codebuild_trigger_lambda"

    @property
    def event_rule_name(self) -> str:
        return f"{self.name_prefix_snake}-codecommit_event_rule"

    @property
    def valid_branch_name_prefix(self) -> str:
        """
        This is the valid branch name prefix that will trigger the codebuild.
        """
        return f"{self.du_name}/"

    @property
    def codebuild_iam_role_name(self) -> str:
        return f"{self.name_prefix_snake}-codebuild"

    @property
    def codepipeline_iam_role_name(self) -> str:
        return f"{self.name_prefix_snake}-codepipeline"

    @property
    def codebuild_project_name(self) -> str:
        return self.name_prefix_snake

    @property
    def codepipeline_pipeline_name(self) -> str:
        return self.name_prefix_snake


# ------------------------------------------------------------------------------
# CDK Stack declaration
# ------------------------------------------------------------------------------
class DeploymentUnitStack(cdk.Stack):
    """
    It includes the following resources.

    - An AWS Lambda function
    - An IAM role for the lambda function
    - An AWS Event Rule that captures CodeCommit reference create / update (create,
        update branch, push commits) events, filter it based on branch name,
        and trigger the above Lambda Function.
    - An AWS Codebuild project that runs CI logic.
    - An IAM role for the Codebuild project
    - An CodePipeline that runs CD logic.
    - An IAM role for the CodePipeline.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        du: DeploymentUnit,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.du = du
        self.declare_resources()

    def declare_resources(self):
        # the IAM role for codebuild trigger lambda function
        self.codebuild_trigger_lambda_role = iam.Role(
            self,
            f"CodeBuildTriggerLambdaRole-{self.du.name_prefix_slug}",
            role_name=self.du.lambda_iam_role_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSCodeBuildDeveloperAccess"
                ),
            ],
        )

        # the trigger lambda function itself
        self.codebuild_trigger_lambda = lambda_.Function(
            self,
            f"CodeBuildTriggerLambda-{self.du.name_prefix_slug}",
            function_name=self.du.lambda_function_name,
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset(path=f"{path_source_zip}"),
            handler="lambda_function.lambda_handler",
            role=self.codebuild_trigger_lambda_role,
            timeout=cdk.Duration.seconds(10),
            memory_size=128,
            environment={
                "AWS_ACCOUNT_ID": cdk.Aws.ACCOUNT_ID,
                "SOURCE_MD5": path_source_zip.md5,
                "DEPLOYMENT_UNIT_NAME": self.du.du_name,
                "DEPLOYMENT_UNIT_NAME_PREFIX": self.du.name_prefix_snake,
                "VALID_BRANCH_NAME_PREFIX": self.du.valid_branch_name_prefix,
                "CODEBUILD_PROJECT_NAME": self.du.codebuild_project_name,
                "CODEPIPELINE_NAME": self.du.codepipeline_pipeline_name,
            },
        )

        # the CodeCommit event rule
        self.codecommit_event_rule = events.Rule(
            self,
            f"CodeCommitEventRule-{self.du.name_prefix_slug}",
            rule_name=self.du.event_rule_name,
            description="Captures CodeCommit Repository State Change",
            # Reference:
            #
            # - Create event example: https://docs.aws.amazon.com/codecommit/latest/userguide/monitoring-events.html#referenceCreated
            # - Update event example: https://docs.aws.amazon.com/codecommit/latest/userguide/monitoring-events.html#referenceUpdated
            # - Content based filtering example: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns-content-based-filtering.html
            event_pattern=events.EventPattern(
                detail_type=[
                    # commit to any branch, create / update branch
                    "CodeCommit Repository State Change",
                ],
                resources=[
                    f"arn:aws:codecommit:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:{self.du.repo_name}",
                ],
                source=["aws.codecommit"],
                detail={
                    "event": [
                        # create commit, create / update branch
                        "referenceCreated",
                        "referenceUpdated",
                    ],
                    "referenceName": [
                        {"prefix": self.du.valid_branch_name_prefix},
                    ],
                },
            ),
            targets=[events_targets.LambdaFunction(self.codebuild_trigger_lambda)],
        )

        # This is the CodeCommit repository where contains this code
        # You should create this CodeCommit repo manuall
        self.i_codecommit_repo = codecommit.Repository.from_repository_name(
            self,
            "Repo",
            self.du.repo_name,
        )
        # This is the CodePipeline Artifact S3 bucket
        # You should create this S3 bucket manually before running CDK
        # The default S3 bucket name is ${aws_account_id}-${aws_region}-codepipeline
        self.i_codepipeline_artifact_bucket = s3.Bucket.from_bucket_name(
            self,
            "ArtifactBucket",
            f"{cdk.Aws.ACCOUNT_ID}-{cdk.Aws.REGION}-codepipeline",
        )

        # the IAM role for codebuild execution
        self.codebuild_run_role = iam.Role(
            self,
            f"CodeBuildRunRole-{self.du.name_prefix_slug}",
            role_name=self.du.codebuild_iam_role_name,
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"),
            ],
        )

        # the CodeBuild project for each deployment unit
        self.codebuild_project = codebuild.Project(
            self,
            f"CodeBuildProject-{self.du.name_prefix_slug}",
            project_name=self.du.codebuild_project_name,
            environment=codebuild.BuildEnvironment(
                # we use AWS Glue 4.0 in this project, which requires Python 3.10
                # We need codebuild ubuntu standard 6.0 image to get Python 3.10
                # See: https://docs.aws.amazon.com/codebuild/latest/userguide/runtime-versions.html
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_4,
                # Small = 3 GB memory, 2 vCPUs
                # Medium = 7 GB memory, 4 vCPUs
                # Large = 15 GB memory, 8 vCPUs
                # See: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-compute-types.html
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables={},
                # Set True if you need to build or use docker image. Otherwise, set False
                privileged=False,
            ),
            build_spec=codebuild.BuildSpec.from_source_filename(
                f"projects/{self.du.du_folder}/buildspec.yml"
            ),
            timeout=cdk.Duration.minutes(30),
            queued_timeout=cdk.Duration.minutes(15),
            concurrent_build_limit=1,
            source=codebuild.Source.code_commit(repository=self.i_codecommit_repo),
            role=self.codebuild_run_role,
            environment_variables={
                # The following environment variables are used in CI logics
                "USER_DEPLOYMENT_UNIT_NAME": codebuild.BuildEnvironmentVariable(
                    value=self.du.du_name,
                ),
                "USER_GIT_REPO_NAME": codebuild.BuildEnvironmentVariable(
                    value=self.du.repo_name,
                ),
            },
        )
        # the CodePipeline execution role
        self.codepipeline_run_role = iam.Role(
            self,
            f"CodePipelineRunRole-{self.du.name_prefix_slug}",
            role_name=self.du.codepipeline_iam_role_name,
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"),
            ],
        )

        # the CodePipeline for each deployment unit
        self.pipeline = codepipeline.Pipeline(
            self,
            f"CodePipeline-{self.du.name_prefix_slug}",
            pipeline_name=self.du.codepipeline_pipeline_name,
            role=self.codepipeline_run_role,
            artifact_bucket=self.i_codepipeline_artifact_bucket,
        )

        source_stage = self.pipeline.add_stage(stage_name="Source")
        source_artifact = codepipeline.Artifact("SourceArtifact")
        source_stage.add_action(
            codepipeline_actions.CodeCommitSourceAction(
                action_name="Source",
                repository=self.i_codecommit_repo,
                # the code pipeline is monitoring the ${du_name}/release branch
                branch=f"{self.du.du_name}/release",
                output=source_artifact,
                trigger=codepipeline_actions.CodeCommitTrigger.EVENTS,
                variables_namespace="SourceVariables",
            )
        )

        for env_name, env_fullname in [
            ("sbx", "Sandbox"),
            ("tst", "Test"),
            ("prd", "Production"),
        ]:
            # Add a manual approval stage for production environment
            if env_name == "prd":
                approve_stage = self.pipeline.add_stage(stage_name="Approve")
                approve_stage.add_action(
                    codepipeline_actions.ManualApprovalAction(
                        action_name="Approve",
                    )
                )

            stage = self.pipeline.add_stage(stage_name=env_fullname)
            codebuild_action = codepipeline_actions.CodeBuildAction(
                action_name=f"{env_fullname}CodeBuildRun",
                project=self.codebuild_project,
                input=source_artifact,
                run_order=1,
                environment_variables={
                    "USER_ENV_NAME": codebuild.BuildEnvironmentVariable(value=env_name),
                    "USER_GIT_BRANCH_NAME": codebuild.BuildEnvironmentVariable(
                        value=f"{self.du.du_name}/release"
                    ),
                    "USER_GIT_COMMIT_ID": codebuild.BuildEnvironmentVariable(
                        value="#{SourceVariables.CommitId}",
                    ),
                    "USER_DEPLOYMENT_UNIT_NAME": codebuild.BuildEnvironmentVariable(
                        value=self.du.du_name,
                    ),
                    "USER_GIT_REPO_NAME": codebuild.BuildEnvironmentVariable(
                        value=self.du.repo_name,
                    ),
                },
            )
            stage.add_action(codebuild_action)


# ------------------------------------------------------------------------------
# CDK synth
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # pre cdk synth
    import sys
    import subprocess

    args = [sys.executable, f"{path_build_lambda_source_py}"]
    subprocess.run(args, check=True)

    # synth stack
    app = cdk.App()

    # initialize the deployment unit stack
    repo_config_data = json.loads(path_repo_config_json.read_text())
    du_config_data = json.loads(path_du_config_json.read_text())
    du = DeploymentUnit(**repo_config_data, **du_config_data)

    stack_name = f"{du.name_prefix_slug}-stack"
    console_url = (
        f"https://console.aws.amazon.com/cloudformation"
        f"/home?#"
        f"/stacks?filteringText={stack_name}&filteringStatus=active&viewNested=true"
    )
    print(f"preview cloudformation stack: {console_url}")
    du_stack = DeploymentUnitStack(
        app,
        construct_id=f"DeploymentUnitStack",
        stack_name=stack_name,
        du=du,
    )

    cdk.Tags.of(app).add("tech:repo_name", du.repo_name)
    cdk.Tags.of(app).add("tech:deployment_unit", du.du_name)
    app.synth()
