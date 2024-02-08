# -*- coding: utf-8 -*-

"""
This is a simple example that has zero dependency, pure python only.
"""

def test():
    assert 1 + 2 == 3


if __name__ == "__main__":
    from simple_glue.tests.glue import run_unit_test

    run_unit_test(__file__, glue_version="4.0")
