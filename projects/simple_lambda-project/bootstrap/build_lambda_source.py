# -*- coding: utf-8 -*-

"""
Build source.zip for codebuild_trigger_lambda. This script will be run in ``app.py``.
"""

from pathlib_mate import Path

dir_here = Path.dir_here(__file__)
dir_codebuild_trigger_lambda = dir_here / "codebuild_trigger_lambda"
path_source_zip = dir_here / "source.zip"

path_source_zip.remove_if_exists()
dir_codebuild_trigger_lambda.make_zip_archive(dst=path_source_zip, include_dir=False)
