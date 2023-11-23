# -*- coding: utf-8 -*-

"""
This lambda function receives CodeCommit events from Event bridge,
analyze the event, then decide whether to trigger CodeBuild or not, and
which CodeBuild project to trigger.

This lambda function has ZERO dependency when Python>=3.7

chore: 52e1daf2e37fdce77a57450fa1489dd7
"""

import typing as T
import os
import json

import boto3

# these are from custom env var
AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]
DEPLOYMENT_UNIT_NAME = os.environ["DEPLOYMENT_UNIT_NAME"]
DEPLOYMENT_UNIT_NAME_PREFIX = os.environ["DEPLOYMENT_UNIT_NAME_PREFIX"]
VALID_BRANCH_NAME_PREFIX = os.environ["VALID_BRANCH_NAME_PREFIX"]
CODEBUILD_PROJECT_NAME = os.environ["CODEBUILD_PROJECT_NAME"]
CODEPIPELINE_NAME = os.environ["CODEPIPELINE_NAME"]

# this one is from built in env var
AWS_REGION = os.environ["AWS_REGION"]

codecommit_client = boto3.client("codecommit")
codebuild_client = boto3.client("codebuild")


def jprint(data):
    text = "\n".join(["| " + line for line in json.dumps(data, indent=4).split("\n")])
    print(text)


def get_commit_message_by_commit_id(
    codecommit_client,
    repo_name: str,
    commit_id: str,
) -> str:
    """
    Get commit message by commit id.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_commit

    :param codecommit_client: boto3.client("codecommit") object
    :param repo_name: CodeCommit repository name
    :param commit_id: the sha256 commit id
    :return: commit message
    """
    res = codecommit_client.get_commit(
        repositoryName=repo_name,
        commitId=commit_id,
    )
    return res["commit"]["message"]


def start_codebuild_job_run(
    codebuild_client,
    codebuild_project_name: str,
    commit_id: str,
    env_vars: T.Dict[str, str],
    repo_name: str,
    deployment_unit_name: str,
) -> dict:
    """
    Run ``codebuild_client.start_build`` API.
    """
    # ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild/client/start_build.html
    res = codebuild_client.start_build(
        projectName=codebuild_project_name,
        sourceVersion=commit_id,
        environmentVariablesOverride=[
            {
                "name": k,
                "value": v,
                "type": "PLAINTEXT",
            }
            for k, v in env_vars.items()
        ],
    )

    # prepare response data
    build_arn = res["build"]["arn"]
    unique_id = build_arn.split("/")[-1]
    console_url = (
        f"https://{AWS_REGION}.console.aws.amazon.com/codesuite/codebuild"
        f"/{AWS_ACCOUNT_ID}/projects/{codebuild_project_name}"
        f"/build/{unique_id}/?region={AWS_REGION}"
    )
    message = (
        f"start a build for repo {repo_name!r}, deployment unit {deployment_unit_name!r}, "
        f"preview at {console_url}"
    )
    return {"message": message}


def handle_repository_state_change_event(event: dict):
    """
    Analyze the event, then decide whether to trigger CodeBuild or not, and
    which CodeBuild project to trigger.

    Reference:

    - https://docs.aws.amazon.com/codecommit/latest/userguide/monitoring-events.html#referenceCreated
    - https://docs.aws.amazon.com/codecommit/latest/userguide/monitoring-events.html#referenceUpdated
    """
    detail = event["detail"]

    # parse repo_name, reference_type, branch_name, commit_id, commit message
    repo_name = detail["repositoryName"]
    reference_type = detail["referenceType"]
    branch_name = detail["referenceName"]
    commit_id = detail["commitId"]
    commit_message = get_commit_message_by_commit_id(
        codecommit_client=codecommit_client,
        repo_name=repo_name,
        commit_id=commit_id,
    )
    commit_message_first_line = commit_message.split("\n")[0]

    print(f"receive a reference change event on {branch_name!r} branch.")
    print(f"commit_id = {commit_id}")
    print(f"commit_message = {commit_message}")

    # prepare the env_vars for codebuild run
    env_vars = {
        "USER_GIT_BRANCH_NAME": branch_name,
        "USER_GIT_COMMIT_ID": commit_id,
        # don't put commit message to env var, because it could has invalid
        # character and it could be multi-lines
        "USER_GIT_COMMIT_MESSAGE": (
            "commit message may have multiple lines so dont fit into env var, "
            "you could use codecommit API to get the message by commit id"
        ),
        "USER_ENV_NAME": "sbx",
    }

    # only trigger build job for create branch or update branch event
    if reference_type != "branch":
        message = f"reference type '{reference_type}' is not 'branch', do nothing."
        return {"message": message}

    # don't trigger build if commit message starts with 'chore'
    if commit_message.lower().startswith("chore"):
        message = (
            f"commit message {commit_message_first_line[:40]!r} starts with 'chore', "
            f"do nothing."
        )
        return {"message": message}

    # the branch name has to follow ${project_name}/${semantic_name} or
    # ${du_name}/${semantic_name}/${description} naming convention
    branch_name_parts = branch_name.split("/")
    if len(branch_name_parts) < 2:
        message = (
            "branch name doesn't follow '${project_name}/${semantic_name}' or "
            "'${project_name}/${semantic_name}/${description}', do nothing"
        )
        return {"message": message}

    # parse deployment_unit_name and semantic_name
    du_name = branch_name_parts[0]
    semantic_name = branch_name_parts[1]

    # analyze the project_name
    # do nothing if the ${project_name} is not recognized
    if du_name != DEPLOYMENT_UNIT_NAME:
        message = (
            f"deployment unit name {du_name!r} is not {DEPLOYMENT_UNIT_NAME!r}, "
            f"do nothing."
        )
        return {"message": message}

    # analyze the semantic_name
    # do nothing if the ${semantic_name} is 'release'
    # this branch is handled by CodePipeline
    if semantic_name in ["release"]:
        return {
            "message": (
                f"The {branch_name!r} is for CodePipeline execution, " f"do nothing."
            )
        }

    # 'chore' branch is designed for doing nothing
    if semantic_name in ["chore"]:
        return {"message": f"Do nothing for {branch_name!r} branch"}

    return start_codebuild_job_run(
        codebuild_client=codebuild_client,
        codebuild_project_name=CODEBUILD_PROJECT_NAME,
        commit_id=commit_id,
        env_vars=env_vars,
        repo_name=repo_name,
        deployment_unit_name=DEPLOYMENT_UNIT_NAME,
    )


def lambda_handler(event: dict, context):
    """
    Todo: add doc string
    """
    print("received event:")
    jprint(event)

    detail_type = event["detail-type"]
    if detail_type == "CodeCommit Repository State Change":
        response = handle_repository_state_change_event(event)
    else:
        response = {"message": f"unknown event type {detail_type!r}, do nothing"}

    print("response:")
    jprint(response)
    return response
