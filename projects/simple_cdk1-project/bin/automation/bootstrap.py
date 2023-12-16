# -*- coding: utf-8 -*-

import json
from pathlib import Path

_dir_here = Path(__file__).absolute().parent
dir_repo_root = _dir_here.parent.parent.parent.parent
path_repo_config = dir_repo_root / "shared" / "repo-config.json"

dir_project_root = _dir_here.parent.parent
path_deployment_unit_config = dir_project_root / "bootstrap" / "du-config.json"

repo_config = json.loads(path_repo_config.read_text())
deployment_unit_config = json.loads(path_deployment_unit_config.read_text())

codecommit_repo_name = repo_config["repo_name"]
repo_name_prefix = repo_config["repo_name_prefix"]
du_name_prefix = deployment_unit_config["du_name_prefix"]
name_prefix_snake = f"{repo_name_prefix}-{du_name_prefix}".replace("-", "_")

codebuild_project_name = name_prefix_snake
codepipeline_pipeline_name = name_prefix_snake
