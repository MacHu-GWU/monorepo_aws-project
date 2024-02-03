# -*- coding: utf-8 -*-

"""
This module implements the automation to display beautiful information using
`rich <https://github.com/Textualize/rich>`_
"""

import typing as T

from rich.table import Table
from rich.text import Text
from rich.style import Style

if T.TYPE_CHECKING: # pragma: no cover
    from pathlib_mate import T_PATH_ARG
    from s3pathlib import S3Path


def file_row(title: str, path: "T_PATH_ARG") -> T.Tuple[Text, Text]:
    """
    Create a table row that presents a file path.
    """
    return (
        Text(str(title), style=Style(link=f"file://{path}")),
        Text(str(path), style=Style(link=f"file://{path}")),
    )


def s3path_row(title: str, s3path: "S3Path") -> T.Tuple[Text, Text]:
    """
    Create a table row that presents an AWS S3 path.
    """
    return (
        Text(title, style=Style(link=s3path.console_url)),
        Text(s3path.console_url, style=Style(link=s3path.console_url)),
    )


def url_row(title: str, url: str) -> T.Tuple[Text, Text]:
    """
    Create a table row that presents an URL.
    """
    return (
        Text(title, style=Style(link=url)),
        Text(url, style=Style(link=url)),
    )


def create_path_table(
    name_and_path_list: T.List[T.Tuple[str, "T_PATH_ARG"]],
    table_title: str = "Important Local Path",
) -> Table:
    """
    Create a table that presents a list of local file path.
    It is the list version of :func:`file_row`.
    """
    table = Table(title=table_title)
    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("Path", no_wrap=True)
    for title, path in name_and_path_list:
        table.add_row(*file_row(title, path))
    return table


def create_s3path_table(
    name_and_s3path_list: T.List[T.Tuple[str, "S3Path"]],
    table_title: str = "Important S3 Location",
) -> Table:
    """
    Create a table that presents a list of AWS S3 path.
    It is the list version of :func:`s3path_row`.
    """
    table = Table(title=table_title)
    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("S3 Console", no_wrap=True)
    for title, s3path in name_and_s3path_list:
        table.add_row(*s3path_row(title, s3path))
    return table


def create_url_table(
    name_and_url_list: T.List[T.Tuple[str, str]],
    table_title: str = "Important Url",
) -> Table:
    """
    Create a table that presents a list of URL.
    It is the list version of :func:`url_row`.
    """
    table = Table(title=table_title)
    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("S3 Console", no_wrap=True)
    for title, url in name_and_url_list:
        table.add_row(*url_row(title, url))
    return table


# Example usage:
if __name__ == "__main__":
    from rich.console import Console
    from s3pathlib import S3Path

    console = Console()

    # ---
    table = create_path_table(
        [("rich_helpers.py", __file__)],
    )
    console.print(table)

    # ---
    table = create_s3path_table(
        [("s3dir_artifacts", S3Path("s3://my-bucket/artifacts/"))],
    )
    console.print(table)

    # ---
    table = create_url_table(
        [("project homepage", "https://my-project.com/")],
    )
    console.print(table)
