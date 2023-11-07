"""Unit tests for modules.custom_error"""
import unittest

import context  # pylint: disable=E0401:import-error
from modules import custom_error


class TestFunction(context.BaseTestCase):
    """Tests for <function_name> function."""

    def test_valid_raise(self):
        """Test successfull raise of TableOperationsError."""
        with self.assertRaises(custom_error.TableOperationsError):
            raise custom_error.TableOperationsError(
                summary="TestSummary",
                message="TestMessage",
            )

    def test_error_repr(self):
        """Test repr of TableOperationsError."""
        error = custom_error.TableOperationsError("summary", "message")

        self.assertEqual(repr(error), "summary: message")

    def test_error_values(self):
        """Test error.summary and error.message of TableOperationsError after raise."""
        try:
            raise custom_error.TableOperationsError("Test Summary", "Test Message")
        except custom_error.TableOperationsError as error:
            self.assertEqual(error.summary, "Test Summary")
            self.assertEqual(error.message, "Test Message")


if __name__ == "__main__":
    unittest.main()
