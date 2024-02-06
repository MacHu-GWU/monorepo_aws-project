# -*- coding: utf-8 -*-

"""
This module implements the automation for AWS Chalice framework.
"""

import typing as T
from datetime import datetime

from ..vendor.hashes import hashes

if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path


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

    :return: a sha256 hash value represent the local lambda source code
    """
    return hashes.of_paths(
        [
            pyproject_ops.path_chalice_config,
            pyproject_ops.path_lambda_app_py,
            pyproject_ops.dir_lambda_app_vendor_python_lib,
        ],
        algo=hashes.AlgoEnum.sha256,
    )


# todo: add concurrency lock mechanism
def download_deployed_json(
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    s3dir_deployed: "S3Path",
) -> bool:
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

    :param env_name:
    :param bsm_devops:
    :param pyproject_ops:
    :param s3dir_deployed: the s3 dir to store the deployed json file.

    :return: a boolean flag to indicate that if the deployed JSON exists on S3
    """
    path_deployed_json = pyproject_ops.dir_lambda_app_deployed / f"{env_name}.json"
    s3path_deployed_json = s3dir_deployed / f"{env_name}.json"

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
    s3dir_deployed: "S3Path",
    source_sha256: T.Optional[str] = None,
    tags: T.Optional[T.Dict[str, str]] = None,
) -> T.Tuple["S3Path", bool]:
    """
    After ``chalice deploy`` succeeded, upload the ``.chalice/deployed/${env_name}.json``
    file from local to s3. It will generate two files:

    1. ``${s3dir_artifacts}/lambda/deployed/${env_name}.json``, this file will
        be overwritten over the time.
    2. ``${s3dir_artifacts}/lambda/deployed/${env_name}-${datetime}.json``, this
        file will stay forever as a backup

    :param env_name:
    :param bsm_devops:
    :param pyproject_ops:
    :param s3dir_deployed: the s3 dir to store the deployed json file.
    :param source_sha256: a sha256 hash value represent the lambda source code digest.
        if not provided, it will be calculated from the source code.
    :param tags: optional AWS resource tags.

    :return: a tuple of the s3 path of the deployed json file
        and a boolean flag to indicate that if the uploaded happen
    """
    path_deployed_json = pyproject_ops.dir_lambda_app_deployed / f"{env_name}.json"
    s3path_deployed_json = s3dir_deployed / f"{env_name}.json"
    # every time we upload the new deployed json file, it overwrites the existing one
    # we want to create a backup before uploading
    time_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S.%f")
    s3path_deployed_json_backup = s3path_deployed_json.change(
        new_basename=f"{env_name}-{time_str}.json"
    )
    if path_deployed_json.exists():
        content = path_deployed_json.read_text()
        if s3path_deployed_json.exists(bsm=bsm_devops):
            if content == s3path_deployed_json.read_text(bsm=bsm_devops):
                return s3path_deployed_json, False
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
        return s3path_deployed_json, True
    else:
        return s3path_deployed_json, False
