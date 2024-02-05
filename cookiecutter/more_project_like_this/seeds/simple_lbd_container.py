# -*- coding: utf-8 -*-

from .. import paths

# declare the path to the seed project
dir_seed_project = paths.dir_projects.joinpath("simple_lbd_container-project")

# declare string mapping and default values for new project
# fmt: off
# mapper = [
#     ("simple_lbd_container", "package_name", "your_package_name"),
#     ("Sanhe Hu", "author_name", "your name"),
#     ("husanhe@gmail.com", "author_email", "your@email.com"),
#     ("bmt-app-devops-us-east-1-doc-host", "doc_host_s3_bucket", "your-doc-host-s3-bucket"),
#     ("0.1.1", "semantic_version", "0.1.1"),
#     ("bmt_app_devops_us_east_1", "devops_aws_profile", "your_aws_profile_for_devops_environment"),
#     ("bmt_app_dev_us_east_1", "sandbox_aws_profile", "your_aws_profile_for_sandbox_environment"),
#     ("bmt_app_test_us_east_1", "test_aws_profile", "your_aws_profile_for_test_environment"),
#     ("bmt_app_prod_us_east_1", "production_aws_profile", "your_aws_profile_for_production_environment"),
#     ("us-east-1", "aws_region", "us-east-1"),
# ]

# I personally use this because I don't want to type too much
mapper = [
    ("simple_lbd_container", "package_name", "your_package_name"),
    ("Sanhe Hu", "author_name", "Sanhe Hu"),
    ("husanhe@gmail.com", "author_email", "husanhe@gmail.com"),
    ("bmt-app-devops-us-east-1-doc-host", "doc_host_s3_bucket", "bmt-app-devops-us-east-1-doc-host"),
    ("0.1.1", "semantic_version", "0.1.1"),
    ("bmt_app_devops_us_east_1", "devops_aws_profile", "bmt_app_devops_us_east_1"),
    ("bmt_app_dev_us_east_1", "sandbox_aws_profile", "bmt_app_dev_us_east_1"),
    ("bmt_app_test_us_east_1", "test_aws_profile", "bmt_app_test_us_east_1"),
    ("bmt_app_prod_us_east_1", "production_aws_profile", "bmt_app_prod_us_east_1"),
    ("us-east-1", "aws_region", "us-east-1"),
]

# fmt: on
# declare files to ignore
exclude = [
    # dir
    ".venv",
    ".pytest_cache",
    ".git",
    ".idea",
    "build",
    "dist",
    "htmlcov",
    "__pycache__",
    "tmp",
    "bootstrap/cdk.out",
    "cdk/cdk.out",
    "lambda_app/.chalice/deployed",
    "lambda_app/.chalice/deployments",
    "lambda_app/vendor",
    "simple_lbd_container/vendor/aws_ops_alpha",
    # file
    ".coverage",
    "*.jinja",
]
