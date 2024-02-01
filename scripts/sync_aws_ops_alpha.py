# -*- coding: utf-8 -*-

import hashlib
from pathlib_mate import Path
from datetime import datetime

dir_project_root = Path.dir_here(__file__).parent
dir_projects = dir_project_root / "projects"


def clear_pycache(dir_aws_ops_alpha: Path):
    for p in dir_aws_ops_alpha.select_file(recursive=True):
        if "__pycache__" in p.abspath:
            p.remove()

def get_last_update_file_and_time(dir_aws_ops_alpha: Path):
    mtime, path = 0, None
    for p in dir_aws_ops_alpha.select_file(recursive=True):
        if p.mtime > mtime:
            mtime, path = p.mtime, p
    return datetime.fromtimestamp(mtime), path

for dir_project in dir_projects.select_dir(recursive=False):
    if dir_project.basename != "dummy_lambda_app-project":
        package_name = dir_project.basename.split("-")[0]
        dir_aws_ops_alpha = dir_project / package_name / "vendor" / "aws_ops_alpha"
        clear_pycache(dir_aws_ops_alpha)
        md5 = dir_aws_ops_alpha.get_dir_fingerprint(hashlib.md5)
        mtime, file = get_last_update_file_and_time(dir_aws_ops_alpha)
        print(dir_project.basename)
        print("- ", md5, mtime, file)

dir_aws_ops_alpha = Path.home().joinpath("Documents/GitHub/aws_ops_alpha-project/aws_ops_alpha")
clear_pycache(dir_aws_ops_alpha)
md5 = dir_aws_ops_alpha.get_dir_fingerprint(hashlib.md5)
mtime, file = get_last_update_file_and_time(dir_aws_ops_alpha)
print(dir_aws_ops_alpha.basename)
print("- ", md5, mtime, file)
