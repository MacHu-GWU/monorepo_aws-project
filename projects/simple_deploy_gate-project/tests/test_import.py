# -*- coding: utf-8 -*-

import os
import pytest
import simple_deploy_gate


def test_import():
    _ = simple_deploy_gate


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
