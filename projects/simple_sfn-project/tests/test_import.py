# -*- coding: utf-8 -*-

import os
import pytest
import simple_sfn


def test_import():
    _ = simple_sfn


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
