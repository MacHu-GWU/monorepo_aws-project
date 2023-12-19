# -*- coding: utf-8 -*-

import os
import pytest
import simple_cdk2


def test_import():
    _ = simple_cdk2


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
