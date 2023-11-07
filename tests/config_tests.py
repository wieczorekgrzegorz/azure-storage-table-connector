"""Unit tests for modules.config"""
import logging
import unittest

import context  # pylint: disable=E0401:import-error
from modules import config

log = logging.getLogger(name="log." + __name__)
logging.basicConfig(level=logging.DEBUG, format="\n%(message)s")


class TestFunctionConstants(context.BaseTestCase):
    """Tests for {FUNCTION_NAME} function."""

    def test_allowed_table_names(self) -> None:
        """Tests if allowed_table_names is a list."""
        self.assertIsInstance(obj=config.ALLOWED_TABLE_NAMES, cls=list)

    def test_allowed_operations(self) -> None:
        """Tests if allowed_operations is a list."""
        self.assertIsInstance(obj=config.ALLOWED_OPERATIONS, cls=list)

    def test_storage_table_connection_string(self) -> None:
        """Tests if storage_table_connection_string is a string."""
        self.assertIsInstance(obj=config.STORAGE_TABLE_CONNECTION_STRING, cls=str)


if __name__ == "__main__":
    unittest.main()
