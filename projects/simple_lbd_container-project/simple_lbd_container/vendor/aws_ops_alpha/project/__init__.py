# -*- coding: utf-8 -*-

"""
This module implements the AWS ops automation steps for various types of projects.
Functions in this module primarily act as wrappers for those in
:mod:`aws_ops_alpha.aws_helpers`, with logging and checks to determine
whether an action should be executed. The parameters in these functions
should be as generic as possible, allowing them to be called in concrete project
source code by passing specific project data.
"""
