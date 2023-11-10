"""Unit tests for modules.utilities.custom_error.py"""
from unittest.mock import patch


from modules.utilities import custom_error
from . import context


class TestTableOperationsError(context.BaseTestCase):
    """Tests for TableOperationsError class."""

    def test_table_operations_error_message(self) -> None:
        """Test TableOperationsError exception message."""
        summary = "SomeError"
        message = "This is an error message"

        try:
            raise custom_error.TableOperationsError(summary=summary, message=message)
        except custom_error.TableOperationsError as e:
            self.assertEqual(first=e.message, second=message)

    def test_table_operations_error_summary(self) -> None:
        """Test TableOperationsError exception summary."""
        summary = "SomeError"
        message = "This is an error message"

        try:
            raise custom_error.TableOperationsError(summary=summary, message=message)
        except custom_error.TableOperationsError as e:
            self.assertEqual(first=e.summary, second=summary)

    def test_table_operations_error_repr(self) -> None:
        """Test TableOperationsError exception repr."""
        summary = "SomeError"
        message = "This is an error message"
        expected_repr = f"{summary}: {message}"

        try:
            raise custom_error.TableOperationsError(summary=summary, message=message)
        except custom_error.TableOperationsError as e:
            self.assertEqual(first=repr(e), second=expected_repr)

    @patch("modules.utilities.custom_error.log")
    def test_table_operations_error_log_exception(self, mock_log) -> None:
        """Test TableOperationsError exception log.exception call."""
        summary = "SomeError"
        message = "This is an error message"
        expected_repr = f"{summary}: {message}"

        try:
            raise custom_error.TableOperationsError(summary=summary, message=message)
        except custom_error.TableOperationsError:
            mock_log.exception.assert_called_once_with(msg=expected_repr, stacklevel=2)


# TODO [KK-189] Storage Table Connector: add tests for custom_error.py
