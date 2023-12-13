from simple_lambda.vendor.aws_ops_alpha.vendor.git_cli import get_git_commit_id_from_git_cli, create_git_tag, push_git_tag
from simple_lambda.paths import dir_project_root

tag_name="v0.0.1"
commit_id = get_git_commit_id_from_git_cli(dir_repo=dir_project_root.parent.parent)
print(f"{commit_id = }")
# create_git_tag(tag_name=tag_name, commit_id=commit_id)
push_git_tag(tag_name)

