# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``step.py`` module should have visualized logging.
"""

# --- standard library
import typing as T
import json

# --- third party library (include vendor)
from boto_session_manager import BotoSesManager
import aws_console_url.api as aws_console_url
import tt4human.api as tt4human
from ...vendor.emoji import Emoji

# --- modules from this project
from ...logger import logger
from ...aws_helpers import aws_chalice_helpers
from ...rule_set import should_we_do_it

# --- modules from this submodule
from .simple_lbd_agw_chalice_truth_table import StepEnum, truth_table

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from s3pathlib import S3Path


@logger.start_and_end(
    msg="Build Lambda Source Chalice Vendor",
    start_emoji=f"{Emoji.build} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.awslambda}",
)
def build_lambda_source_chalice_vendor(
    pyproject_ops: "pyops.PyProjectOps",
):
    logger.info(
        f"review source artifacts at local: {pyproject_ops.dir_lambda_app_vendor_python_lib}"
    )
    aws_chalice_helpers.build_lambda_source_chalice_vendor(pyproject_ops=pyproject_ops)


@logger.start_and_end(
    msg="Download lambda_app/.chalice/deployed/{env_name}.json from S3",
    start_emoji=Emoji.awslambda,
    error_emoji=f"{Emoji.failed} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def download_deployed_json(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    s3dir_deployed: "S3Path",
    check=True,
    step: str = StepEnum.deploy_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
) -> bool:
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return False

    s3path_deployed_json = s3dir_deployed / f"{env_name}.json"
    logger.info(f"try to download existing deployed {env_name}.json file")
    logger.info(f"from {s3path_deployed_json.s3_select_console_url}")
    flag = aws_chalice_helpers.download_deployed_json(
        env_name=env_name,
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        s3dir_deployed=s3dir_deployed,
    )
    if flag is False:
        logger.info("no existing deployed json file found, SKIP download.")
    return flag


@logger.start_and_end(
    msg="Upload deployed/$env_name.json to S3",
    start_emoji=Emoji.awslambda,
    error_emoji=f"{Emoji.failed} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def upload_deployed_json(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    s3dir_deployed: "S3Path",
    source_sha256: T.Optional[str] = None,
    tags: T.Optional[T.Dict[str, str]] = None,
    check=True,
    step: str = StepEnum.deploy_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
) -> T.Tuple["S3Path", bool]:
    s3path_deployed_json = s3dir_deployed / f"{env_name}.json"

    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return s3path_deployed_json, False

    logger.info(
        f"upload the deployed {env_name}.json file to "
        f"{s3path_deployed_json.console_url}"
    )
    s3path_deployed_json, flag = aws_chalice_helpers.upload_deployed_json(
        env_name=env_name,
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        s3dir_deployed=s3dir_deployed,
        source_sha256=source_sha256,
        tags=tags,
    )
    if flag is False:
        logger.error("no existing deployed json file found, skip upload", indent=1)
    return s3path_deployed_json, flag


@logger.start_and_end(
    msg="Run 'chalice {command} --stage {env_name}' command",
    start_emoji=f"{Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def run_chalice_command(
    env_name: str,
    command: str,
    chalice_app_name: str,
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
):
    res = aws_chalice_helpers.run_chalice_command(
        env_name=env_name,
        command=command,
        bsm_devops=bsm_devops,
        bsm_workload=bsm_workload,
        pyproject_ops=pyproject_ops,
    )
    if res.returncode == 0:
        pass
    else:
        logger.info(f"return code: {res.returncode}", indent=1)
        logger.error(f"{Emoji.error} 'chalice {command}' failed!")
        logger.info(res.stdout.decode("utf-8"))
        logger.error(res.stderr.decode("utf-8"))
        raise SystemError

    # print console url
    func_prefix = f"{chalice_app_name}-{env_name}"
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    url = aws_console.awslambda.filter_functions(func_prefix)
    logger.info(f"preview deployed lambda functions: {url}")


@logger.start_and_end(
    msg="Deploy Chalice App to {env_name!r} environment",
    start_emoji=f"{Emoji.deploy} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def run_chalice_deploy(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    chalice_app_name: str,
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    s3dir_deployed: "S3Path",
    tags: T.Optional[T.Dict[str, str]] = None,
    check=True,
    step: str = StepEnum.deploy_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):
    """
    Deploy lambda app using chalice.

    The workflow is as follows:

    1. build lambda source code for ``lambda_app/vendor/${package_name}`` folder.
    2. run ``update_chalice_config.py`` script to update ``.chalice/config.json`` file.
    3. download the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
    4. run ``chalice deploy`` command to deploy the lambda function.
    5. upload the ``lambda_app/.chalice/deployed/${env_name}.json`` file.

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param chalice_app_name: the chalice app name, it will be used as part of the
        lambda function naming convention.
    :param s3dir_deployed: the s3dir to store the deployed json file.
    :param project_name: the project name, it will be used as the AWS resources tag.
    :param prod_env_name: the production environment name, it will be used to
        prompt user to confirm if they want to deploy to production environment.
    :param env_name: the environment name, specify which stage of chalice app
        to deploy, it will be used as part of the lambda function naming convention.
    :param check: whether to check if we should run chalice deploy command.
    """
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return False

    # 1. build lambda source code for ``lambda_app/vendor/${package_name}`` folder.
    with logger.nested():
        build_lambda_source_chalice_vendor(pyproject_ops=pyproject_ops)

    # 2. run ``update_chalice_config.py`` script to update ``.chalice/config.json`` file.
    logger.info(f"{Emoji.python} run 'update_chalice_config.py' ...")
    aws_chalice_helpers.run_update_chalice_config_script(pyproject_ops=pyproject_ops)
    source_sha256 = aws_chalice_helpers.get_source_sha256(pyproject_ops=pyproject_ops)

    if check:
        is_same = aws_chalice_helpers.is_current_lambda_code_the_same_as_deployed_one(
            bsm_devops=bsm_devops,
            s3dir_deployed=s3dir_deployed,
            env_name=env_name,
            source_sha256=source_sha256,
        )
        if is_same:
            logger.info(
                f"{Emoji.red_circle} don't run 'chalice deploy', "
                f"the local lambda source code is the same as the deployed one.",
            )
            return False

    with logger.nested():
        # 3. download the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
        download_deployed_json(
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            s3dir_deployed=s3dir_deployed,
            check=check,
            step=step,
            truth_table=truth_table,
            url=url,
        )
        # 4. run ``chalice deploy`` command to deploy the lambda function.
        run_chalice_command(
            env_name=env_name,
            command="deploy",
            chalice_app_name=chalice_app_name,
            bsm_devops=bsm_devops,
            bsm_workload=bsm_workload,
            pyproject_ops=pyproject_ops,
        )
        # 5. upload the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
        upload_deployed_json(
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            s3dir_deployed=s3dir_deployed,
            source_sha256=source_sha256,
            tags=tags,
            check=check,
            step=step,
            truth_table=truth_table,
            url=url,
        )

    return True


@logger.start_and_end(
    msg="Delete Chalice App from {env_name!r} environment",
    start_emoji=f"{Emoji.delete} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def run_chalice_delete(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    chalice_app_name: str,
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    s3dir_deployed: "S3Path",
    tags: T.Optional[T.Dict[str, str]] = None,
    check=True,
    step: str = StepEnum.deploy_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):
    """
    Delete lambda app using chalice.

    The workflow is as follows:

    1. create dummy ``.chalice/config.json`` file.
    2. download the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
    3. run ``chalice delete`` command to delete the lambda function.
    4. upload the ``lambda_app/.chalice/deployed/${env_name}.json`` file.

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param chalice_app_name: the chalice app name, it will be used as part of the
        lambda function naming convention.
    :param s3dir_deployed: the s3dir to store the deployed json file.
    :param project_name: the project name, it will be used as the AWS resources tag.
    :param prod_env_name: the production environment name, it will be used to
        prompt user to confirm if they want to deploy to production environment.
    :param env_name: the environment name, specify which stage of chalice app
        to deploy, it will be used as part of the lambda function naming convention.
    :param check: whether to check if we should run chalice deploy command.
    """
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return False

    # 1. create dummy ``.chalice/config.json`` file.
    logger.info(f"{Emoji.python} create dummy '.chalice/config.json' ...")
    pyproject_ops.path_chalice_config.write_text(json.dumps({"version": "2.0"}))

    with logger.nested():
        # 2. download the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
        download_deployed_json(
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            s3dir_deployed=s3dir_deployed,
            check=check,
            step=step,
            truth_table=truth_table,
            url=url,
        )
        # 3. run ``chalice delete`` command to delete the lambda function.
        run_chalice_command(
            env_name=env_name,
            command="delete",
            chalice_app_name=chalice_app_name,
            bsm_devops=bsm_devops,
            bsm_workload=bsm_workload,
            pyproject_ops=pyproject_ops,
        )
        # 4. upload the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
        upload_deployed_json(
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            s3dir_deployed=s3dir_deployed,
            source_sha256="deleted by chalice delete command",
            tags=tags,
            check=check,
            step=step,
            truth_table=truth_table,
            url=url,
        )

    return True
