# -*- coding: utf-8 -*-

"""
Show essential project information.
"""

from rich.table import Table
from rich.text import Text
from rich.style import Style

from .logger import logger, console
from .emoji import Emoji
from .pyproject import pyproject_ops
from .bootstrap import (
    codecommit_repo_name,
    codebuild_project_name,
    codepipeline_pipeline_name,
)


def show_path(name, path):
    console.print("| | ", Text(name, style="green"), Text(str(path), style="red"))


def _file(title, path) -> tuple:
    return (
        Text(str(title), style=Style(link=f"file://{path}")),
        Text(str(path), style=Style(link=f"file://{path}")),
    )


def _s3path(title, s3path) -> tuple:
    return (
        Text(title, style=Style(link=s3path.console_url)),
        # Text(s3path.uri, style=Style(link=s3path.console_url)),
        Text(s3path.console_url, style=Style(link=s3path.console_url)),
    )


def _url(title, url) -> tuple:
    return (
        Text(title, style=Style(link=url)),
        Text(url, style=Style(link=url)),
    )


def show_important_paths():
    table = Table(title="Important Local Paths")

    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("Path", no_wrap=True)

    table.add_row(*_file("dir_project_root", pyproject_ops.dir_project_root))
    table.add_row(*_file("dir_python_lib", pyproject_ops.dir_python_lib))
    table.add_row(*_file("dir_venv", pyproject_ops.dir_venv))
    table.add_row(*_file("path_venv_bin_python", pyproject_ops.path_venv_bin_python))
    table.add_row(*_file("path_config_json", pyproject_ops.path_config_json))
    table.add_row(*_file("path_secret_config_json", pyproject_ops.path_secret_config_json))
    table.add_row(*_file("dir_tests", pyproject_ops.dir_tests))
    table.add_row(*_file("dir_docs", pyproject_ops.dir_sphinx_doc_source))

    console.print(table)


def show_important_s3_location():
    from simple_lambda.config.init import config

    table = Table(title="Important S3 Location")

    table.add_column("Title", style="cyan", no_wrap=True)
    # table.add_column("S3 Uri", no_wrap=True)
    table.add_column("S3 Console", no_wrap=True)

    table.add_row(*_s3path("s3dir_artifacts", config.env.s3dir_artifacts))
    table.add_row(*_s3path("s3dir_data", config.env.s3dir_data))
    table.add_row(*_s3path("s3dir_config", config.env.s3dir_config))
    table.add_row(*_s3path("s3dir_lambda", config.env.s3dir_lambda))

    console.print(table)


def show_important_aws_console_url():
    from aws_console_url import AWSConsole

    from simple_lambda.config.init import config
    from simple_lambda.boto_ses import bsm

    aws = AWSConsole(
        aws_account_id=bsm.aws_account_id,
        aws_region=bsm.aws_region,
        bsm=bsm,
    )

    table = Table(title="Important AWS Console Url")

    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("Url", no_wrap=True)

    table.add_row(*_url("codecommit", aws.codecommit.get_repo(codecommit_repo_name)))
    table.add_row(*_url("codebuild", aws.codebuild.get_project(codebuild_project_name)))
    table.add_row(
        *_url(
            "codepipeline",
            (
                f"https://{bsm.aws_region}.console.aws.amazon.com/codesuite/codepipeline"
                f"/pipelines/{codepipeline_pipeline_name}/view?region={bsm.aws_region}"
            ),
        )
    )
    url = aws.ssm.filter_parameters(config.parameter_name)
    table.add_row(*_url("parameter store", url))
    url = aws.cloudformation.filter_stack(config.project_name_slug)
    table.add_row(*_url("cloudformation stacks", url))
    url = aws.awslambda.filter_functions(config.project_name)
    table.add_row(*_url("lambda functions", url))
    url = aws.awslambda.get_layer(config.env.lambda_layer_name)
    table.add_row(*_url("lambda layer", url))

    console.print(table)


def show_project_info():
    show_important_paths()

    try:
        show_important_s3_location()
    except ImportError:
        pass

    try:
        show_important_aws_console_url()
    except ImportError:
        pass


@logger.start_and_end(
    msg="Run Unit Test",
    start_emoji=Emoji.eye,
    error_emoji=f"{Emoji.failed} {Emoji.eye}",
    end_emoji=f"{Emoji.succeeded} {Emoji.eye}",
    pipe=Emoji.eye,
)
def show_runtime_env_git_info():
    from .runtime import print_runtime_info
    from .env import print_env_info
    from .git import print_git_info

    print_runtime_info()
    print_env_info()
    print_git_info()
