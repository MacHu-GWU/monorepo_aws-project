# -*- coding: utf-8 -*-

"""
CI/CD workflow typically follows a sequence of steps. Some steps are mandatory,
such as "install dependencies," while others are optional, like "run integration tests."

In order to determine whether a step should be executed, we need to consider
the following factors:

- On which Git branch (feature, release, etc.) are we working?
- In which environment (DevOps, sbx, tst, stg, prd) are we?
- At which runtime (local laptop, CI) are we?

This module provides a clean API for the end user to identify whether a step
should be executed. It helps avoid writing numerous if-else statements in the code.

For the maintainers of the ``aws_ops_alpha`` Python library, this module also
offers a neat way to manage the truth table in a Google Sheet and synchronize
the code implementation with the data in Google Sheet.
"""

import typing as T
import csv
import enum
import string
import dataclasses
from pathlib import Path

from ..vendor.emoji import Emoji

from ..logger import logger


# the charset and normalized_text method are used to clean up the invalid characters
# in Google Sheet (like emoji) and make the text in a Python variable name friendly format
charset: T.Set[str] = set(
    string.digits + string.ascii_letters + string.punctuation + " "
)


def normalize_text(text: str) -> T.Union[str, bool]:
    """
    Example:

        >>> normalize_text("🐍 Create Virtualenv")
        'Create Virtualenv'
    """
    chars = [c for c in text if c in charset]
    text = "".join(chars)
    return " ".join([word.strip() for word in text.split() if word.strip()])


# type hint variables
T_INDICES = T.List[str]
T_COLUMNS = T.List[str]
T_DATA = T.List[T.List[T.Any]]
T_FLAGS = T.List[T.List[bool]]
T_LOOKUP = T.Dict[str, T.Dict[str, bool]]


def read_tsv(path: Path) -> T.Tuple[T_INDICES, T_COLUMNS, T_DATA]:
    """
    Read the list of rows data from a TSV file.

    Example tsv::

        # tsv file content
                col1    col2    col3
        row1    1       2       3
        row2    4       5       6

    Example output::

        (
            ["row1", "row2"],           # indices
            ["col1", "col2", "col3"],   # columns
            [                           # data
                ["1", "2", "3"],
                ["4", "5", "6"],
            ]
        ]
    """
    with path.open("r") as f:
        reader = csv.reader(f, delimiter="\t")
        rows = list(reader)
    columns = rows[0][1:]
    if len(set(columns)) != len(columns):  # pragma: no cover
        raise ValueError("Duplicate value in headers")
    indices = []
    data = []
    for row in rows[1:]:
        indices.append(row[0])
        data.append(row[1:])
    return indices, columns, data


def extract_steps(indices: T_INDICES) -> T.List[str]:
    return [normalize_text(index).upper().replace(" ", "_") for index in indices]


def extract_conditions(columns: T_COLUMNS) -> T.List[str]:
    """
    Valid condition type are git_branch_name, env_name, runtime_name.
    """
    return [normalize_text(col).lower() for col in columns]


_emoji_to_bool_mapper = {
    "✅": True,
    "❌": False,
}


def extract_flags(data: T_DATA) -> T.List[T.List[bool]]:
    """
    We use emoji to represent True/False in Google Sheet. This function
    converts the emoji to boolean values.
    """
    return [[_emoji_to_bool_mapper[v] for v in row] for row in data]


class TruthTableNameEnum(str, enum.Enum):
    """
    Enumerate type of truth table. The ``${truth_table}.tsv`` file name has to match
    this enum class.
    """

    git_branch_name = "git_branch_name"
    env_name = "env_name"
    runtime_name = "runtime_name"


@dataclasses.dataclass
class TruthTable:
    """
    Represent a two dimension truth table. The row is the step name, and the column
    is the condition name. The value is a boolean value indicating whether the step
    should be executed under the condition.

    :param steps:
    :param conditions:
    :param flags:
    :param mapper: an in-memory mapper to quickly look up the flag value
    """

    steps: T.List[str] = dataclasses.field()
    conditions: T.List[str] = dataclasses.field()
    flags: T_FLAGS = dataclasses.field()
    mapper: T_LOOKUP = dataclasses.field()

    @classmethod
    def from_tsv(cls, path_tsv: Path):
        """
        Read the truth table from a TSV file.
        """
        indices, columns, data = read_tsv(path_tsv)
        steps = extract_steps(indices)
        conditions = extract_conditions(columns)
        flags = extract_flags(data)
        mapper = dict()
        for step, row in zip(steps, flags):
            dct = {condition: flag for condition, flag in zip(conditions, row)}
            mapper[step] = dct
        return cls(steps=steps, conditions=conditions, flags=flags, mapper=mapper)

    def get_flag(self, step: str, condition: str) -> bool:
        """
        Get the flag value for a step and a condition.
        """
        return self.mapper.get(step, {}).get(condition, False)


def snake_to_camel(text: str) -> str:  # pragma: no cover
    """
    Convert snake case to camel case.
    """
    return text.title().replace("_", "")


no_go_message_template = (
    f"{Emoji.red_circle} don't {{step}}, "
    f"your {{truth_table_name!r}} is {{condition_value!r}}, "
    f"we don't do it on this. "
    f"You can enter the 'aws_ops_alpha display {{rule_set_name}}' command "
    f"in your terminal to see the rule set truth table."
)


@dataclasses.dataclass
class RuleSet:
    """
    Represent a set of rules to determine whether a step should be executed.

    A rule set consists of a list of truth tables. We will use all the truth tables
    to evaluate the step and its conditions. Only when all truth tables return 'True',
    the step will be executed.

    :param path_folder: the folder path of the rule set
    :param name: the rule set name
    :param steps: a list of step names
    :param truth_table_mapper: map the truth table name to the truth table object
    """

    path_folder: Path = dataclasses.field()
    name: str = dataclasses.field()
    steps: T.List[str] = dataclasses.field()
    truth_table_mapper: T.Dict[str, TruthTable] = dataclasses.field()

    @classmethod
    def from_folder(cls, path_folder: Path):
        """
        Read all related truth tables from a folder.
        """
        truth_table_mapper = dict()
        steps: T.Optional[T.List[str]] = None
        truth_table_steps_fingerprint_list = []
        for truth_table_name in TruthTableNameEnum:
            path_tsv = path_folder / f"{truth_table_name}.tsv"
            truth_table = TruthTable.from_tsv(path_tsv)
            truth_table_mapper[truth_table_name.value] = truth_table
            steps = truth_table.steps
            truth_table_steps_fingerprint_list.append("----".join(steps))

        if len(set(truth_table_steps_fingerprint_list)) != 1:  # pragma: no cover
            raise ValueError("The steps in all truth tables must be the same.")

        return cls(
            path_folder=path_folder,
            name=path_folder.name,
            steps=steps,
            truth_table_mapper=truth_table_mapper,
        )

    def should_we_do_it(
        self,
        step: str,
        git_branch_name: str,
        env_name: str,
        runtime_name: str,
        verbose: bool = True,
    ) -> bool:
        """
        Get the flag value for a step and conditions. If the answer is False,
        we may display some helpful message to the user.
        """
        truth_table_name_and_condition_value_list = [
            (TruthTableNameEnum.git_branch_name.value, git_branch_name),
            (TruthTableNameEnum.env_name.value, env_name),
            (TruthTableNameEnum.runtime_name.value, runtime_name),
        ]
        for (
            truth_table_name,
            condition_value,
        ) in truth_table_name_and_condition_value_list:
            flag = self.truth_table_mapper[truth_table_name].get_flag(
                step=step,
                condition=condition_value,
            )
            if flag is False:
                if verbose:  # pragma: no cover
                    logger.info(
                        no_go_message_template.format(
                            step=step,
                            truth_table_name=truth_table_name,
                            condition_value=condition_value,
                            rule_set_name=self.name,
                        )
                    )
                return flag
        return True

    def get_flag(
        self,
        step: str,
        git_branch_name: str,
        env_name: str,
        runtime_name: str,
    ) -> bool:
        """
        Get the flag value for a step and conditions.
        """
        return self.should_we_do_it(
            step,
            git_branch_name,
            env_name,
            runtime_name,
            verbose=False,
        )

    def generate_code(self):  # pragma: no cover
        """
        Generate source code for the given rule set.
        """
        import jinja2

        # generate constants.py
        template = jinja2.Template(path_constants_py_jinja.read_text())
        content = template.render(rule_set=self, snake_to_camel=snake_to_camel)
        path_constants_py = self.path_folder / "constants.py"
        path_constants_py.write_text(content)

    def display(self, verbose: bool = True):
        """
        Display the rule set definition.
        """
        from rich.table import Table
        from rich.text import Text
        from ..logger import console

        _bool_to_symbol_mapper = {
            True: Text("+", style="green"),
            False: Text("-", style="red"),
        }

        for truth_table_name, truth_table in self.truth_table_mapper.items():
            table = Table(title=f"step and {truth_table_name}")
            table.add_column(f"steps / {truth_table_name}")
            # col1 = f"steps / {truth_table_name}"
            # width = max(
            #     len(col1),
            #     max([len(step) for step in truth_table.steps]),
            # )
            # table.add_column(f"steps / {truth_table_name}", width=width)
            for v in truth_table.conditions:
                table.add_column(Text(v, style="cyan"), justify="center")
            for step, flag_list in zip(truth_table.steps, truth_table.flags):
                table.add_row(
                    Text(step, style="cyan"),
                    *[_bool_to_symbol_mapper[flag] for flag in flag_list],
                )
            if verbose:  # pragma: no cover
                console.print(table)


dir_rule = Path(__file__).absolute().parent
path_constants_py_jinja = dir_rule / "constants.py.jinja"
