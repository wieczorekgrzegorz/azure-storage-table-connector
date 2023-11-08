"""Unit tests for modules.custom_error"""
import unittest

import context  # pylint: disable=E0401:import-error
from modules import custom_error


class TestFunction(context.BaseTestCase):
    """Tests for <function_name> function."""

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=C0103:invalid-name
        """Extends setUpClass from BaseTestCase. Adds class attributes common for all tests in this module."""
        cls.error_summary = "Test error summary"
        cls.error_message = "This is test error message."
        cls.expected_repr = f"TableOperationsError(summary={cls.error_summary}, message={cls.error_message})"
        cls.expected_string = f"{cls.error_summary}: {cls.error_message}"
        super().setUpClass()

    def test_valid_raise(self) -> None:
        """Test successfull raise of TableOperationsError."""
        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            raise custom_error.TableOperationsError(
                summary=self.error_summary,
                message=self.error_message,
            )
        self.assertEqual(first=repr(cm.exception), second=self.expected_repr)

    def test_proper_class_attributes_assignment(self) -> None:
        """Test error.summary and error.message of TableOperationsError after raise."""
        error = custom_error.TableOperationsError(summary=self.error_summary, message=self.error_message)

        self.assertEqual(first=error.summary, second=self.error_summary)
        self.assertEqual(first=error.message, second=self.error_message)

    def test_error_repr(self) -> None:
        """Test repr of TableOperationsError."""
        error = custom_error.TableOperationsError(summary=self.error_summary, message=self.error_message)
        self.assertEqual(first=repr(error), second=self.expected_repr)

    def test_error_str(self) -> None:
        """Test str of TableOperationsError."""
        error = custom_error.TableOperationsError(summary=self.error_summary, message=self.error_message)
        self.assertEqual(first=str(object=error), second=self.expected_string)


if __name__ == "__main__":
    unittest.main()
