# -*- coding: utf-8 -*-

"""
This module implements the automation for AWS Chalice framework.
"""

# --- standard library
import typing as T
import subprocess
from pathlib import Path
from datetime import datetime

# --- third party library (include vendor)
import aws_lambda_layer.api as aws_lambda_layer
from boto_session_manager import BotoSesManager, PATH_DEFAULT_SNAPSHOT
from ..vendor.hashes import HashAlgoEnum, hashes
from ..vendor.aws_s3_lock import Lock, Vault, AlreadyLockedError

# --- modules from this project
from ..constants import EnvVarNameEnum
from ..env_var import temp_env_var

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from s3pathlib import S3Path


def build_lambda_source_chalice_vendor(
    pyproject_ops: "pyops.PyProjectOps",
):
    """
    Copy the Lambda source code Python library from
    ``${dir_project_root}/${package_name}`` to
    ``${dir_project_root}/lambda_app/vendor/${package_name}``.

    It also removes the ``__pycache__`` directory and the ``.pyc``, ``.pyo``
    files during the copy.

    :param pyproject_ops: ``PyProjectOps`` object.
    """
    aws_lambda_layer.build_source_python_lib(
        dir_python_lib_source=pyproject_ops.dir_python_lib,
        dir_python_lib_target=pyproject_ops.dir_lambda_app_vendor_python_lib,
    )


def get_source_sha256(
    pyproject_ops: "pyops.PyProjectOps",
) -> str:
    """
    The ``chalice deploy`` command is an expensive operation, even when
    there is no change in the source code.

    During the initial ``chalice deploy``, we calculate the SHA256 hash of the
    related source code and store it in the metadata of the deployed JSON file in S3.

    Subsequent ``chalice deploy`` operations involve comparing the SHA256 hash
    of the source code with the one stored in the S3 metadata. If the two hashes
    are the same, we skip the ``chalice deploy`` operation.

    The SHA256 hash is calculated from the following files (order does matter):

    - lambda_app/.chalice/config.json
    - lambda_app/app.py
    - lambda_app/vendor/${package_name}

    :param pyproject_ops: ``PyProjectOps`` object.

    :return: a sha256 hash value represent the local lambda source code
    """
    return hashes.of_paths(
        [
            pyproject_ops.path_chalice_config,
            pyproject_ops.path_lambda_app_py,
            pyproject_ops.dir_lambda_app_vendor_python_lib,
        ],
        algo=HashAlgoEnum.sha256,
    )


def is_current_lambda_code_the_same_as_deployed_one(
    bsm_devops: "BotoSesManager",
    s3path_deployed_json: "S3Path",
    source_sha256: str,
) -> bool:  # pragma: no cover
    """
    Compare the local chalice app source code hash with the deployed one.

    :param env_name: the environment name
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param s3path_deployed_json: the S3 path to the deployed ``${env_name}.json`` file.
    :param source_sha256: a sha256 hash value represent the local lambda source code

    :return: a boolean flag to indicate that if the local lambda source code
        is the same as the deployed one.
    """
    if s3path_deployed_json.exists(bsm=bsm_devops):
        existing_source_sha256 = s3path_deployed_json.metadata["source_sha256"]
        return source_sha256 == existing_source_sha256
    else:
        return False


def get_concurrency_lock(
    vault: Vault,
    owner: str,
    bsm_devops: "BotoSesManager",
) -> T.Optional[Lock]:# pragma: no cover
    """
    Get the concurrency lock.

    :return: True if got the lock, False if not
    """
    try:
        lock = vault.acquire(s3_client=bsm_devops.s3_client, owner=owner)
        return lock
    except AlreadyLockedError:
        return None


def download_deployed_json(
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    s3path_deployed_json: "S3Path",
) -> bool: # pragma: no cover
    """
    AWS Chalice utilizes a ``deployed/${env_name}.json`` JSON file to store
    the deployed resource information.

    Since this file is generated on the fly based on the project config file,
    it cannot be stored in the Git repository. A better approach is to use S3
    as the centralized storage for this file. Whenever we perform a new
    ``chalice deploy`` operation, we attempt to download the latest
    deployed JSON file from S3, carry out the deployment, and then
    upload the updated JSON file back to S3.

    Naturally, we employ a concurrency lock mechanism to prevent competition.

    :param env_name: the environment name
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param s3path_deployed_json: the S3 path to the deployed ``${env_name}.json`` file.

    :return: a boolean flag to indicate that if the deployed JSON exists on S3
    """
    path_deployed_json = pyproject_ops.dir_lambda_app_deployed / f"{env_name}.json"

    # pull the existing deployed json file from s3
    if s3path_deployed_json.exists(bsm=bsm_devops):
        pyproject_ops.dir_lambda_app_deployed.mkdir(parents=True, exist_ok=True)
        path_deployed_json.write_text(s3path_deployed_json.read_text(bsm=bsm_devops))
        return True
    # there's no deployed json file on s3, skip the download
    else:
        return False


def upload_deployed_json(
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    s3path_deployed_json: "S3Path",
    source_sha256: T.Optional[str] = None,
    tags: T.Optional[T.Dict[str, str]] = None,
) -> bool:  # pragma: no cover
    """
    After ``chalice deploy`` succeeded, upload the ``.chalice/deployed/${env_name}.json``
    file from local to s3. It will generate two files:

    1. ``${s3dir_artifacts}/lambda/deployed/${env_name}.json``, this file will
        be overwritten over the time.
    2. ``${s3dir_artifacts}/lambda/deployed/${env_name}-${datetime}.json``, this
        file will stay forever as a backup

    :param env_name: env name, will be used for conditional step test.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param s3path_deployed_json: the S3 path to the deployed ``${env_name}.json`` file.
    :param source_sha256: a sha256 hash value represent the lambda source code digest.
        if not provided, it will be calculated from the source code.
    :param tags: optional AWS resource tags.

    :return: a tuple of the s3 path of the deployed json file
        and a boolean flag to indicate that if the uploaded happen
    """
    path_deployed_json = pyproject_ops.dir_lambda_app_deployed / f"{env_name}.json"
    # every time we upload the new deployed json file, it overwrites the existing one
    # we want to create a backup before uploading
    time_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S.%f")
    s3path_deployed_json_backup = s3path_deployed_json.change(
        new_fname=f"{s3path_deployed_json.fname}-{time_str}"
    )
    if path_deployed_json.exists():
        content = path_deployed_json.read_text()
        if s3path_deployed_json.exists(bsm=bsm_devops):
            if content == s3path_deployed_json.read_text(bsm=bsm_devops):
                return False
        if source_sha256 is None:
            source_sha256 = get_source_sha256(pyproject_ops)
        kwargs = dict(
            data=content,
            content_type="application/json",
            metadata={"source_sha256": source_sha256},
            bsm=bsm_devops,
        )
        if tags:
            kwargs["tags"] = tags
        s3path_deployed_json_backup.write_text(**kwargs)
        s3path_deployed_json.write_text(**kwargs)
        return True
    else:
        return False


def run_chalice_command(
    env_name: str,
    command: str,
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    path_bsm_devops_snapshot: Path = PATH_DEFAULT_SNAPSHOT,
) -> subprocess.CompletedProcess:  # pragma: no cover
    """
    Run ``chalice deploy`` or ``chalice delete`` command to deploy / delete
    the lambda function and API Gateway.
    """
    path_venv_bin_chalice = pyproject_ops.dir_venv_bin / "chalice"
    args = [
        f"{path_venv_bin_chalice}",
        "--project-dir",
        f"{pyproject_ops.dir_lambda_app}",
        command,
        "--stage",
        env_name,
    ]
    with bsm_devops.temp_snapshot(path=path_bsm_devops_snapshot):
        with bsm_workload.awscli():
            with temp_env_var({EnvVarNameEnum.USER_ENV_NAME.value: env_name}):
                res = subprocess.run(args, capture_output=True)
    return res


def run_update_chalice_config_script(
    pyproject_ops: "pyops.PyProjectOps",
):  # pragma: no cover
    """
    Run the following command to generate ``.chalice/config.json`` file.

    .. code-block:: bash

        ./.venv/bin/python lambda_app/update_chalice_config.py
    """
    args = [
        f"{pyproject_ops.path_venv_bin_python}",
        f"{pyproject_ops.path_lambda_update_chalice_config_script}",
    ]
    subprocess.run(args, check=True)
