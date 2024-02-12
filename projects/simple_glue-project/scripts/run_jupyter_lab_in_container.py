# -*- coding: utf-8 -*-

"""
Requirements:

    aws_glue_container_launcher>=0.1.2,<1.0.0
"""

import subprocess
from pathlib_mate import Path

import boto3
from aws_glue_container_launcher.api import (
    GlueVersionEnum,
    build_jupyter_lab_args,
)

dir_here = Path(__file__).absolute().parent
dir_project_root = dir_here.parent
dir_venv = dir_project_root / ".venv"
path_bin_pip = dir_venv / "bin" / "pip"
path_requirements_glue_local_dev_txt = dir_here / "requirements_glue_local_dev.txt"
dir_glue_site_packages = dir_here.joinpath("glue_site_packages")
container_name = "simple_glue_local_jupyter_lab_for_glue"

if __name__ == "__main__":
    # create a clean site-packages folder for glue local dev
    with dir_project_root.temp_cwd():
        args = [
            f"{path_bin_pip}",
            "install",
            "--no-deps",
            "-t",
            f"{dir_glue_site_packages}",
            ".",
        ]
        subprocess.run(args, check=True)

    args = [
        f"{path_bin_pip}",
        "install",
        "-t",
        f"{dir_glue_site_packages}",
        "-r",
        f"{path_requirements_glue_local_dev_txt}",
    ]
    subprocess.run(args, check=True)

    args = build_jupyter_lab_args(
        dir_home=Path.home(), # the ${HOME}/.aws directory will be mounted to the container
        dir_workspace=dir_project_root,
        container_name=container_name,
        auto_remove_container=True,
        glue_version=GlueVersionEnum.GLUE_4_0.value,
        # you may not use all dependencies of the project in site-packages,
        # because they may have conflict with the AWS Glue container pre-installed packages.
        # A better way is to install your source code and only Glue related dependencies
        # to a folder other than the .venv/lib/python3.9/site-packages,
        # you can use pip install -t command to do so.
        dir_site_packages=dir_glue_site_packages,
        boto_session=boto3.session.Session(profile_name="bmt_app_dev_us_east_1"),
        spark_ui_port=4041,
        spark_history_server_port=18081,
        livy_server_port=8999,
        jupyter_notebook_port=8889,
        enable_hudi=True,
        additional_docker_run_args=None,
        additional_env_vars=None,
    )
    print(" ".join(args))
    subprocess.run(args)
