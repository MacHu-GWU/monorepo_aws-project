# -*- coding: utf-8 -*-

"""
由于我们的 DevOps 核心逻辑都在 aws_ops_alpha 项目中，而为了开发方便, 我们会:

1. 在 monorepo_aws 这个项目中直接对 ``${project_name}-project/${project_name}/vendor/aws_ops_alpha/`` 目录
进行修改.
2. 然后手动将其拷贝到 ``aws_ops_alpha-project/aws_ops_alpha/`` 中.
3. 然后再用这个脚本将其同步到所有其他项目中.
"""

import hashlib
import shutil
from pathlib_mate import Path
from datetime import datetime

dir_project_root = Path.dir_here(__file__).parent
dir_projects = dir_project_root / "projects"
dir_aws_ops_alpha_project_source = Path.home().joinpath(
    "Documents/GitHub/aws_ops_alpha-project/aws_ops_alpha"
)


def clear_pycache(dir_aws_ops_alpha: Path):
    for p in dir_aws_ops_alpha.select_file(recursive=True):
        if "__pycache__" in p.abspath:
            p.remove()


def get_dir_md5(dir_aws_ops_alpha: Path) -> str:
    """
    把所有的文件先按照 path 排序, 然后把它们的 md5 值拼接起来，然后取拼接后的字符串的 md5 值.
    """
    m = hashlib.md5()
    for p in dir_aws_ops_alpha.sort_by_abspath(
        dir_aws_ops_alpha.select_file(recursive=True)
    ):
        m.update(p.md5.encode("utf-8"))
    return m.hexdigest()


def get_last_update_file_and_time(dir_aws_ops_alpha: Path):
    """
    获得目录下最后更新的文件的时间和路径.
    """
    mtime, path = 0, None
    for p in dir_aws_ops_alpha.select_file(recursive=True):
        if p.mtime > mtime:
            mtime, path = p.mtime, p
    return datetime.fromtimestamp(mtime), path


def check_aws_ops_alpha_md5():
    """
    打印所有项目中的的 aws_ops_alpha 目录的 MD5 值.
    """
    for dir_project in dir_projects.select_dir(recursive=False):
        if dir_project.basename != "dummy_lambda_app-project":
            package_name = dir_project.basename.split("-")[0]
            dir_aws_ops_alpha = dir_project / package_name / "vendor" / "aws_ops_alpha"
            clear_pycache(dir_aws_ops_alpha)
            md5 = get_dir_md5(dir_aws_ops_alpha)
            mtime, file = get_last_update_file_and_time(dir_aws_ops_alpha)
            print(dir_project.basename)
            print("- ", md5, mtime, file)

    clear_pycache(dir_aws_ops_alpha_project_source)
    md5 = get_dir_md5(dir_aws_ops_alpha_project_source)
    mtime, file = get_last_update_file_and_time(dir_aws_ops_alpha_project_source)
    print(dir_aws_ops_alpha_project_source.basename)
    print("- ", md5, mtime, file)


def sync_aws_ops_alpha():
    """
    将 aws_ops_alpha-project/aws_ops_alpha 目录同步到所有项目中.
    """
    source_project = "simple_glue"
    source_dir = dir_project_root / "projects" / f"{source_project}-project" / source_project / "vendor" / "aws_ops_alpha"
    for dir_project in dir_projects.select_dir(recursive=False):
        if dir_project.basename != "dummy_lambda_app-project":
            if dir_project.basename != f"{source_project}-project":
                package_name = dir_project.basename.split("-")[0]
                dir_aws_ops_alpha = dir_project / package_name / "vendor" / "aws_ops_alpha"
                dir_aws_ops_alpha.remove_if_exists()
                shutil.copytree(source_dir, dir_aws_ops_alpha)
    dir_aws_ops_alpha_project_source.remove_if_exists()
    shutil.copytree(source_dir, dir_aws_ops_alpha_project_source)

# check_aws_ops_alpha_md5()
# sync_aws_ops_alpha()
