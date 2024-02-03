# -*- coding: utf-8 -*-

"""
Git CLI related utilities.

Usage example::

    from fixa.git_cli import (
        temp_cwd,
        GitCLIError,
        locate_dir_repo,
        get_git_branch_from_,git_cli
        get_git_commit_id_fr,om_git_cli
        get_commit_message_b,y_commit_id
        create_local_git_tag,
        delete_local_git_tag,
    )
"""

import typing as T
import os
import subprocess
import contextlib
from pathlib import Path

__version__ = "0.2.1"


@contextlib.contextmanager
def temp_cwd(path: T.Union[str, Path]):  # pragma: no cover
    """
    Temporarily set the current working directory (CWD) and automatically
    switch back when it's done.

    Example:

    .. code-block:: python

        with temp_cwd(Path("/path/to/target/working/directory")):
            # do something

    .. versionadded:: 0.1.1
    """
    path = Path(path).absolute()
    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a dir!")
    cwd = os.getcwd()
    os.chdir(str(path))
    try:
        yield path
    finally:
        os.chdir(cwd)


class GitCLIError(Exception):
    """
    .. versionadded:: 0.1.1
    """

    pass


def locate_dir_repo(path: Path) -> Path:
    """
    Locate the directory of the git repository. Similar to the effect of
    ``git rev-parse --show-toplevel``.

    .. versionadded:: 0.1.1
    """
    if path.joinpath(".git").exists():
        return path
    if path.parent == path:
        raise FileNotFoundError("Cannot find the .git folder!")
    return locate_dir_repo(path.parent)


def get_git_branch_from_git_cli(
    dir_repo: T.Union[str, Path],
) -> str:
    """
    Use ``git`` CLI to get the current git branch.

    Run:

    .. code-block:: bash

        cd $dir_repo
        git branch --show-current

    .. versionadded:: 0.1.1
    """
    try:
        with temp_cwd(dir_repo):
            args = ["git", "branch", "--show-current"]
            res = subprocess.run(args, capture_output=True, check=True)
            branch = res.stdout.decode("utf-8").strip()
            return branch
    except Exception as e:  # pragma: no cover
        raise GitCLIError(str(e))


def get_git_commit_id_from_git_cli(
    dir_repo: T.Union[str, Path],
) -> str:
    """
    Use ``git`` CIL to get current git commit id.

    Run:

    .. code-block:: bash

        cd $dir_repo
        git rev-parse HEAD

    .. versionadded:: 0.1.1
    """
    try:
        with temp_cwd(dir_repo):
            args = ["git", "rev-parse", "HEAD"]
            res = subprocess.run(
                args,
                capture_output=True,
                check=True,
            )
            commit_id = res.stdout.decode("utf-8").strip()
            return commit_id
    except Exception as e:  # pragma: no cover
        raise GitCLIError(str(e))


def get_commit_message_by_commit_id(
    dir_repo: T.Union[str, Path],
    commit_id: str,
) -> str:
    """
    Get the first line of commit message.

    Run:

    .. code-block:: bash

        cd $dir_repo
        git log --format=%B -n 1 ${commit_id}

    .. versionadded:: 0.1.1
    """
    try:
        with temp_cwd(dir_repo):
            args = ["git", "log", "--format=%B", "-n", "1", commit_id]
            response = subprocess.run(args, capture_output=True, check=True)
    except Exception as e:  # pragma: no cover
        raise GitCLIError(str(e))
    message = response.stdout.decode("utf-8")
    message = message.strip().split("\n")[0].replace("'", "").replace('"', "").strip()
    return message


def create_local_git_tag(
    dir_repo: T.Union[str, Path],
    tag_name: str,
    commit_id: str,
):
    """
    Create a local git tag.

    Reference:

    - https://git-scm.com/book/en/v2/Git-Basics-Tagging

    Run:

    .. code-block:: bash

        cd $dir_repo
        git tag ${tag_name}

    .. versionadded:: 0.2.1
    """
    with temp_cwd(dir_repo):
        args = [
            "git",
            "tag",
            tag_name,
            commit_id,
        ]
        subprocess.run(args, check=True)


def delete_local_git_tag(
    dir_repo: T.Union[str, Path],
    tag_name: str,
):
    """
    Delete a local git tag.

    Reference:

    - https://git-scm.com/book/en/v2/Git-Basics-Tagging

    Run:

    .. code-block:: bash

        cd $dir_repo
        git tag -d ${tag_name}

    .. versionadded:: 0.2.1
    """
    with temp_cwd(dir_repo):
        args = [
            "git",
            "tag",
            "-d",
            tag_name,
        ]
        subprocess.run(args, check=True)
