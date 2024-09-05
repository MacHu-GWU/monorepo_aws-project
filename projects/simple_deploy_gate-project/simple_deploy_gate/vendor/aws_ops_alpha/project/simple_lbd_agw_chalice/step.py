# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``step.py`` module should have visualized logging.
"""

# --- standard library
import typing as T
import json
import uuid

# --- third party library (include vendor)
from boto_session_manager import BotoSesManager
import aws_console_url.api as aws_console_url
import tt4human.api as tt4human
from ...vendor.emoji import Emoji
from ...vendor.aws_s3_lock import Lock, Vault

# --- modules from this project
from ...logger import logger
from ...aws_helpers.api import aws_chalice_helpers
from ...rule_set import should_we_do_it

# --- modules from this submodule
from .simple_lbd_agw_chalice_truth_table import StepEnum, truth_table as tt

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
):  # pragma: no cover
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
    s3path_deployed_json: "S3Path",
    check=True,
    step: str = StepEnum.deploy_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = None,
    url: T.Optional[str] = None,
) -> bool:  # pragma: no cover
    """
    See :func:`aws_ops_alpha.aws_helpers.aws_chalice_helpers.download_deployed_json`.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param s3path_deployed_json: the S3 path to the deployed ``${env_name}.json`` file.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=tt if truth_table is None else truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return False

    logger.info(f"try to download existing deployed {env_name}.json file")
    logger.info(f"from {s3path_deployed_json.s3_select_console_url}")
    flag = aws_chalice_helpers.download_deployed_json(
        env_name=env_name,
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        s3path_deployed_json=s3path_deployed_json,
    )
    if flag is False:
        logger.info("no existing deployed json file found, SKIP download.")
    return flag


@logger.start_and_end(
    msg="Upload deployed/{env_name}.json to S3",
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
    s3path_deployed_json: "S3Path",
    source_sha256: T.Optional[str] = None,
    tags: T.Optional[T.Dict[str, str]] = None,
    check=True,
    step: str = StepEnum.deploy_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = None,
    url: T.Optional[str] = None,
) -> bool:  # pragma: no cover
    """
    See :func:`aws_ops_alpha.aws_helpers.aws_chalice_helpers.upload_deployed_json`.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param s3path_deployed_json: the S3 path to the deployed ``${env_name}.json`` file.
    :param tags: optional AWS resource tags.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=tt if truth_table is None else truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return False

    logger.info(
        f"upload the deployed {env_name}.json file to "
        f"{s3path_deployed_json.console_url}"
    )
    flag = aws_chalice_helpers.upload_deployed_json(
        env_name=env_name,
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        s3path_deployed_json=s3path_deployed_json,
        source_sha256=source_sha256,
        tags=tags,
    )
    if flag is False:
        logger.error(
            "the deployed json file not changed "
            "or no existing deployed json file found, skip upload",
            indent=1,
        )
    return flag


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
):  # pragma: no cover
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
    msg="Try to get lock for owner {owner}",
    start_emoji=f"{Emoji.lock}",
    error_emoji=f"{Emoji.lock}",
    end_emoji=f"{Emoji.succeeded} {Emoji.lock}",
    pipe=Emoji.lock,
)
def get_lock(
    vault: Vault,
    owner: str,
    bsm_devops: "BotoSesManager",
) -> T.Optional[Lock]:  # pragma: no cover
    """
    Get the concurrency lock.

    :return: True if got the lock, False if not.
    """
    logger.info(f"try to get the concurrency lock ...")
    lock = aws_chalice_helpers.get_concurrency_lock(
        vault=vault, owner=owner, bsm_devops=bsm_devops
    )
    if lock is None:
        with logger.indent():
            logger.info("it's already locked, skip chalice deploy.")
    else:
        with logger.indent():
            logger.info("got it.")
    return lock


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
    s3path_deployed_json: "S3Path",
    tags: T.Optional[T.Dict[str, str]] = None,
    check=True,
    step: str = StepEnum.deploy_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = None,
    url: T.Optional[str] = None,
) -> bool:  # pragma: no cover
    """
    Deploy lambda app using chalice.

    The workflow is as follows:

    1. build lambda source code for ``lambda_app/vendor/${package_name}`` folder.
    2. run ``update_chalice_config.py`` script to update ``.chalice/config.json`` file.
    3. download the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
    4. run ``chalice deploy`` command to deploy the lambda function.
    5. upload the ``lambda_app/.chalice/deployed/${env_name}.json`` file.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param chalice_app_name: the chalice app name, it will be used as part of the
        lambda function naming convention.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param bsm_workload: the workload AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param s3path_deployed_json: the S3 path to the deployed ``${env_name}.json`` file.
    :param tags: optional AWS resource tags.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.

    :return: a boolean flag to indicate whether it runs ``chalice deploy`` command.
    """
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=tt if truth_table is None else truth_table,
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
            s3path_deployed_json=s3path_deployed_json,
            source_sha256=source_sha256,
        )
        if is_same:
            logger.info(
                f"{Emoji.red_circle} don't run 'chalice deploy', "
                f"the local lambda source code is the same as the deployed one.",
            )
            return False

    s3dir_lock = s3path_deployed_json.parent.joinpath("lock")
    owner = uuid.uuid4().hex
    s3path_lock = s3dir_lock.joinpath(f"{owner}.lock")
    vault = Vault(bucket=s3path_lock.bucket, key=s3path_lock.key, expire=600, wait=0.1)

    with logger.nested():
        # 3. download the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
        if get_lock(vault=vault, owner=owner, bsm_devops=bsm_devops) is None:
            return False
        download_deployed_json(
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            s3path_deployed_json=s3path_deployed_json,
            check=check,
            step=step,
            truth_table=truth_table,
            url=url,
        )
        # 4. run ``chalice deploy`` command to deploy the lambda function.
        if get_lock(vault=vault, owner=owner, bsm_devops=bsm_devops) is None:
            return False
        run_chalice_command(
            env_name=env_name,
            command="deploy",
            chalice_app_name=chalice_app_name,
            bsm_devops=bsm_devops,
            bsm_workload=bsm_workload,
            pyproject_ops=pyproject_ops,
        )
        # 5. upload the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
        lock = get_lock(vault=vault, owner=owner, bsm_devops=bsm_devops)
        if lock is None:
            return False
        upload_deployed_json(
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            s3path_deployed_json=s3path_deployed_json,
            source_sha256=source_sha256,
            tags=tags,
            check=check,
            step=step,
            truth_table=truth_table,
            url=url,
        )
        logger.info(f"release the lock")
        vault.release(s3_client=bsm_devops.s3_client, lock=lock)
        s3dir_lock.delete(bsm=bsm_devops)
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
    s3path_deployed_json: "S3Path",
    tags: T.Optional[T.Dict[str, str]] = None,
    check=True,
    step: str = StepEnum.delete_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = None,
    url: T.Optional[str] = None,
) -> bool:  # pragma: no cover
    """
    Delete lambda app using chalice.

    The workflow is as follows:

    1. create dummy ``.chalice/config.json`` file.
    2. download the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
    3. run ``chalice delete`` command to delete the lambda function.
    4. upload the ``lambda_app/.chalice/deployed/${env_name}.json`` file.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param chalice_app_name: the chalice app name, it will be used as part of the
        lambda function naming convention.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param bsm_workload: the workload AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param s3path_deployed_json: the S3 path to the deployed ``${env_name}.json`` file.
    :param tags: optional AWS resource tags.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.

    :return: a boolean flag to indicate whether it runs ``chalice delete`` command.
    """
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=tt if truth_table is None else truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return False

    # 1. create dummy ``.chalice/config.json`` file.
    # chalice don't need to know the configuration data to delete, it just needs
    # this file to locate the app.py location.
    logger.info(f"{Emoji.python} create dummy '.chalice/config.json' ...")
    pyproject_ops.path_chalice_config.write_text(json.dumps({"version": "2.0"}))

    s3dir_lock = s3path_deployed_json.parent.joinpath("lock")
    owner = uuid.uuid4().hex
    s3path_lock = s3dir_lock.joinpath(f"{owner}.lock")
    vault = Vault(bucket=s3path_lock.bucket, key=s3path_lock.key, expire=600, wait=0.1)

    with logger.nested():
        # 2. download the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
        if get_lock(vault=vault, owner=owner, bsm_devops=bsm_devops) is None:
            return False
        download_deployed_json(
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            s3path_deployed_json=s3path_deployed_json,
            check=check,
            step=step,
            truth_table=truth_table,
            url=url,
        )
        # 3. run ``chalice delete`` command to delete the lambda function.
        if get_lock(vault=vault, owner=owner, bsm_devops=bsm_devops) is None:
            return False
        run_chalice_command(
            env_name=env_name,
            command="delete",
            chalice_app_name=chalice_app_name,
            bsm_devops=bsm_devops,
            bsm_workload=bsm_workload,
            pyproject_ops=pyproject_ops,
        )
        # 4. upload the ``lambda_app/.chalice/deployed/${env_name}.json`` file.
        lock = get_lock(vault=vault, owner=owner, bsm_devops=bsm_devops)
        if lock is None:
            return False
        upload_deployed_json(
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            s3path_deployed_json=s3path_deployed_json,
            source_sha256="deleted by chalice delete command",
            tags=tags,
            check=check,
            step=step,
            truth_table=truth_table,
            url=url,
        )
        logger.info(f"release the lock")
        vault.release(s3_client=bsm_devops.s3_client, lock=lock)
        s3dir_lock.delete(bsm=bsm_devops)

    return True
