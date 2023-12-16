# -*- coding: utf-8 -*-

"""
Semantic branch is a git branch naming convention to indicate what you are
trying to do on the git branch. Also, CI system can use branch name to
figure out what to do.

semantic git branch name format::

    ${semantic_name}-${optional_marker}/${description}/${more_slash_is_ok}

Sample valid semantic git branch name syntax::

    main
    feature
    feature/add-this-feature
    feature-123/description
    release/1.2.3

Usage example::

    import fixa.semantic_branch as sem_branch

    _ = sem_branch.InvalidSemanticNameError
    _ = sem_branch.SemanticBranchEnum
    _ = is_valid_semantic_name
    _ = ensure_is_valid_semantic_name
    _ = sem_branch.is_certain_semantic_branch
    _ = sem_branch.is_main_branch
    _ = sem_branch.is_feature_branch
    _ = sem_branch.is_build_branch
    _ = sem_branch.is_doc_branch
    _ = sem_branch.is_fix_branch
    _ = sem_branch.is_release_branch
    _ = sem_branch.is_cleanup_branch
    _ = sem_branch.is_sandbox_branch
    _ = sem_branch.is_develop_branch
    _ = sem_branch.is_test_branch
    _ = sem_branch.is_int_branch
    _ = sem_branch.is_staging_branch
    _ = sem_branch.is_qa_branch
    _ = sem_branch.is_preprod_branch
    _ = sem_branch.is_prod_branch
    _ = sem_branch.is_blue_branch
    _ = sem_branch.is_green_branch
    _ = sem_branch.SemanticBranchRule
"""

import typing as T
import enum
import string
import dataclasses

__version__ = "0.2.1"


class InvalidSemanticNameError(ValueError):
    """
    Raised when the semantic branch name is invalid.
    """


class SemanticBranchEnum(str, enum.Enum):
    """
    Semantic branch name enumeration.
    """

    main = "main"
    master = "master"

    # based on purpose
    feat = "feat"
    feature = "feature"
    build = "build"
    doc = "doc"
    fix = "fix"
    hotfix = "hotfix"
    rls = "rls"
    release = "release"
    clean = "clean"
    cleanup = "cleanup"

    # based on environment
    sbx = "sbx"
    sandbox = "sandbox"
    dev = "dev"
    develop = "develop"
    tst = "tst"
    test = "test"
    int = "int"
    stg = "stg"
    stage = "stage"
    staging = "staging"
    qa = "qa"
    preprod = "preprod"
    prd = "prd"
    prod = "prod"
    blue = "blue"
    green = "green"


semantic_name_charset = set(string.ascii_lowercase + string.digits)


def is_valid_semantic_name(name: str):
    """
    Valid semantic name should only contain lowercase letters and digits.
    """
    return len(set(name).difference(semantic_name_charset)) == 0


def ensure_is_valid_semantic_name(name: str) -> str:  # pragma: no cover
    """
    Raise an exception if the name is not a valid semantic name.
    Otherwise, return it as it is.
    """
    if is_valid_semantic_name(name) is False:
        raise InvalidSemanticNameError(f"{name!r} is not a valid semantic name")
    return name


def is_certain_semantic_branch(name: str, words: T.List[str]) -> bool:
    """
    Test if a branch name meet certain semantic rules.

    Below is an example to check if the branch name start with the keyword "feature"::

        >>> is_certain_semantic_branch(
        ...     name="feature/add-this-feature",
        ...     stub=["feat", "feature"],
        ... )
        True

    :param name: branch name
    :param words: semantic words

    :return: a boolean value
    """
    name = name.lower().strip()
    name = name.split("/")[0]
    name = name.split("-")[0]
    words = set([ensure_is_valid_semantic_name(word.lower().strip()) for word in words])
    return name in words


def is_main_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.main,
            SemanticBranchEnum.master,
        ],
    )


def is_feature_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.feat,
            SemanticBranchEnum.feature,
        ],
    )


def is_build_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.build,
        ],
    )


def is_doc_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.doc,
        ],
    )


def is_fix_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.fix,
        ],
    )


def is_release_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.rls,
            SemanticBranchEnum.release,
        ],
    )


def is_cleanup_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.clean,
            SemanticBranchEnum.cleanup,
        ],
    )


def is_sandbox_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.sbx,
            SemanticBranchEnum.sandbox,
        ],
    )


def is_develop_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.dev,
            SemanticBranchEnum.develop,
        ],
    )


def is_test_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.tst,
            SemanticBranchEnum.test,
        ],
    )


def is_int_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.int,
        ],
    )


def is_staging_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.stg,
            SemanticBranchEnum.stage,
            SemanticBranchEnum.staging,
        ],
    )


def is_qa_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.qa,
        ],
    )


def is_preprod_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.preprod,
        ],
    )


def is_prod_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.prd,
            SemanticBranchEnum.prod,
        ],
    )


def is_blue_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.blue,
        ],
    )


def is_green_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.green,
        ],
    )


def _default_preprocessor(git_branch_name: str) -> str:
    return git_branch_name


@dataclasses.dataclass
class SemanticBranchRule:
    """
    A pre-defined semantic branch rule that only accept certain semantic branch names.

    Example::

        >>> semantic_branch_rule = SemanticBranchRule(
        ...     rules={
        ...         "main": ["main", "master"],
        ...         "feature": ["feat", "feature"],
        ...     }
        ... )

    :param rules: a python dictionary that the key is the valid semantic name
        in this rule, the value is a list of keywords that can be used to identify
        this semantic name
    :param preprocessor: a function that can transform the git branch name before
        sending to :meth:`SemanticBranchRulel.is_certain_semantic_branch`` method
    :param _parse_semantic_name_cache: an internal cache to store the result of
        :meth:`SemanticBranchRulel.parse_semantic_name` method. End user should not
        use it.
    """

    # fmt: off
    rules: T.Dict[str, T.List[str]] = dataclasses.field()
    preprocessor: T.Callable[[str], str] = dataclasses.field(default=_default_preprocessor)
    _parse_semantic_name_cache: T.Dict[str, str] = dataclasses.field(default_factory=dict)
    # fmt: on

    def is_certain_semantic_branch(
        self,
        git_branch_name: str,
        semantic_name: str,
    ) -> bool:
        """
        Test if a branch name meet certain semantic name rules.

        Example::

            >>> semantic_branch_rule = SemanticBranchRule(
            ...     rules={
            ...         "main": ["main", "master"],
            ...         "feature": ["feat", "feature"],
            ...     }
            ... )
            >>> semantic_branch_rule.is_certain_semantic_branch(git_branch_name="main", semantic_name="main")
            True
            >>> semantic_branch_rule.is_certain_semantic_branch(git_branch_name="major", semantic_name="main")
            False
            >>> semantic_branch_rule.is_certain_semantic_branch(git_branch_name="feature/description", semantic_name="feature")
            True
            >>> semantic_branch_rule.is_certain_semantic_branch(git_branch_name="feature-123/description", semantic_name="feature")
            True
            >>> semantic_branch_rule.is_certain_semantic_branch(git_branch_name="release", semantic_name="release")
            InvalidSemanticNameError: semantic name 'major' doesn't match any semantic name in ['main', 'feature']
        """
        try:
            keywords = self.rules[semantic_name]
            return is_certain_semantic_branch(git_branch_name, keywords)
        except KeyError:
            raise InvalidSemanticNameError(
                f"semantic name {semantic_name!r} doesn't match any semantic name in {list(self.rules)!r}"
            )

    def parse_semantic_name(self, git_branch_name: str) -> str:
        """
        Parse a branch name to a semantic name. If the branch name doesn't match any
        rules, raise an exception.

        Example::

            >>> semantic_branch_rule = SemanticBranchRule(
            ...     rules={
            ...         "main": ["main", "master"],
            ...         "feature": ["feat", "feature"],
            ...     }
            ... )
            >>> semantic_branch_rule.parse_semantic_name("main")
            'main'
            >>> semantic_branch_rule.parse_semantic_name("feature/123")
            'feature'
            >>> semantic_branch_rule.parse_semantic_name("feature-123/123")
            'feature'
            >>> semantic_branch_rule.parse_semantic_name("release")
            InvalidSemanticNameError: branch 'major' doesn't match any semantic name in ['main', 'feature']
        """
        if git_branch_name in self._parse_semantic_name_cache:
            return self._parse_semantic_name_cache[git_branch_name]

        git_branch_name = self.preprocessor(git_branch_name)
        for semantic_name, keywords in self.rules.items():
            if is_certain_semantic_branch(git_branch_name, keywords):
                self._parse_semantic_name_cache[git_branch_name] = semantic_name
                return semantic_name

        raise InvalidSemanticNameError(
            f"branch {git_branch_name!r} doesn't match any semantic name in {list(self.rules)!r}"
        )
