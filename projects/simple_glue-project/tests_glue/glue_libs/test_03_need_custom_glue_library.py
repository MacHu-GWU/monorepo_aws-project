# -*- coding: utf-8 -*-

"""
This example depends on your custom Glue Python Library, and it might depends on
other 3rd party library.
"""

from simple_glue.glue_libs.utils import add_two


def test():
    assert add_two(1, 2) == 3


if __name__ == "__main__":
    from simple_glue.tests.glue import run_unit_test

    run_unit_test(__file__, glue_version="4.0")
