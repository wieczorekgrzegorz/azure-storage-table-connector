"""Unit tests for modules.main"""
import unittest
from unittest.mock import Mock, patch, MagicMock

import azure.functions


import context  # pylint: disable=E0401:import-error
from modules import main, custom_error


class TestFunction(context.BaseTestCase):
    """Tests for <function_name> function."""


if __name__ == "__main__":
    unittest.main()
