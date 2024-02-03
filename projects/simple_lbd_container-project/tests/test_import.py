# -*- coding: utf-8 -*-

import os
import pytest
import simple_lbd_container


def test_import():
    _ = simple_lbd_container


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
