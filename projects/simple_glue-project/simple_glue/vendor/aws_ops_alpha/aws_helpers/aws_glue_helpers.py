# -*- coding: utf-8 -*-

"""
This module implements the automation to manage AWS Glue artifacts, unit tests, etc ...
"""

import typing as T
import subprocess

from versioned.api import Artifact
from aws_glue_artifact.api import GluePythonLibArtifact, GlueETLScriptArtifact


if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager


def build_glue_extra_py_files_artifact(
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    glue_python_lib_artifact: "GluePythonLibArtifact",
    tags: T.Optional[T.Dict[str, str]] = None,
) -> "Artifact":  # pragma: no cover
    kwargs = dict(
        bsm=bsm_devops,
        metadata={
            "package_version": pyproject_ops.package_version,
        },
    )
    if tags:
        kwargs["tags"] = tags
    return glue_python_lib_artifact.put_artifact(**kwargs)


def publish_glue_extra_py_files_artifact_version(
    bsm_devops: "BotoSesManager",
    glue_python_lib_artifact: "GluePythonLibArtifact",
) -> "Artifact":  # pragma: no cover
    return glue_python_lib_artifact.publish_artifact_version(bsm=bsm_devops)


def build_glue_script_artifact(
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    glue_etl_script_artifact_list: T.List["GlueETLScriptArtifact"],
    tags: T.Optional[T.Dict[str, str]] = None,
) -> T.List["Artifact"]:  # pragma: no cover
    artifact_list = list()
    metadata = {
        "package_version": pyproject_ops.package_version,
    }
    for glue_etl_script_artifact in glue_etl_script_artifact_list:
        kwargs = dict(
            bsm=bsm_devops,
            metadata=metadata,
        )
        if tags:
            kwargs["tags"] = tags
        artifact = glue_etl_script_artifact.put_artifact(**kwargs)
        artifact_list.append(artifact)
    return artifact_list


def publish_glue_script_artifact_version(
    bsm_devops: "BotoSesManager",
    glue_etl_script_artifact_list: T.List["GlueETLScriptArtifact"],
) -> T.List["Artifact"]:  # pragma: no cover
    artifact_list = list()
    for glue_etl_script_artifact in glue_etl_script_artifact_list:
        artifact = glue_etl_script_artifact.publish_artifact_version(bsm=bsm_devops)
        artifact_list.append(artifact)
    return artifact_list


def run_glue_unit_test(
    pyproject_ops: "pyops.PyProjectOps",
):  # pragma: no cover
    args = [
        f"{pyproject_ops.path_venv_bin_python}",
        str(pyproject_ops.dir_project_root.joinpath("tests_glue", "all.py")),
    ]
    subprocess.run(args, check=True)


def run_glue_int_test(
    pyproject_ops: "pyops.PyProjectOps",
):  # pragma: no cover
    args = [
        f"{pyproject_ops.path_venv_bin_python}",
        str(pyproject_ops.dir_project_root.joinpath("tests_glue_int", "all.py")),
    ]
    subprocess.run(args, check=True)
