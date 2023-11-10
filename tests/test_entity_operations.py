"""Unit tests for config.py"""
import unittest
from unittest.mock import Mock, patch, MagicMock

import azure.functions


import context
from modules import custom_error, get_req_body


class TestFunction(context.BaseTestCase):
    """Tests for <function_name> function."""


# TODO [KK-190]  Storage Table Connector: add tests for enitity_operations.py
