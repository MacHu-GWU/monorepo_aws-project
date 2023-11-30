# -*- coding: utf-8 -*-

"""
Note: this is the only module that import the step. This step doesn't have
any Python dependencies. For other step, we use CLI to run the step, so we
can use any Python to run those step scripts, they will find the virtualenv
Python automatically.
"""

from python_lib.steps.s1_setup_venv import main

main()
