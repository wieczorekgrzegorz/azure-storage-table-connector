"""Unit tests for get_req_body_tests.py"""
import datetime
import unittest
from unittest.mock import Mock, patch, MagicMock

import azure.functions


import context  # pylint: disable=E0401:import-error
from modules import get_req_body
from modules.utilities import custom_error


class TestReqToJson(context.BaseTestCase):
    """Tests for req_to_json function."""

    def test_req_to_json_valid(self) -> None:
        """Test if req_to_json returns valid JSON."""
        mock_request = Mock(spec=azure.functions.HttpRequest)
        mock_request.get_json.return_value = {"key": "value"}

        result = get_req_body.req_to_json(req=mock_request)

        self.assertEqual(first=result, second={"key": "value"})

    def test_req_to_json_invalid(self) -> None:
        """Test if req_to_json raises TableOperationsError when request does not contain valid JSON data."""
        mock_request = Mock(spec=azure.functions.HttpRequest)
        mock_request.get_json.side_effect = ValueError("Invalid JSON")
        expected_error_summary = "RequestError"
        expected_error_message = "HTTP request does not contain valid JSON data. Please check your request body."

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.req_to_json(req=mock_request)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)


class TestParseReqBody(context.BaseTestCase):
    """Tests for parse_req_body function."""

    def test_parse_req_body_valid(self) -> None:
        """Test if parse_req_body returns valid tuple."""
        req_body = {"entity": {"key": "value"}, "table_name": "test_table", "operation": "insert"}

        result = get_req_body.parse_req_body(req_body=req_body)

        self.assertEqual(first=result, second=({"key": "value"}, "test_table", "insert"))

    def test_parse_req_body_key_error(self) -> None:
        """Test if parse_req_body raises TableOperationsError when request does not contain valid JSON data."""
        req_body = {"entity": {"key": "value"}, "operation": "insert"}
        expected_error_summary = "RequestError"
        expected_error_message = "KeyError while parsing request body: 'table_name' not found."

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.parse_req_body(req_body=req_body)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)

    def test_parse_req_body_type_error(self) -> None:
        """Test if parse_req_body raises TableOperationsError when request does not contain valid JSON data."""
        req_body = "not a dictionary"
        expected_error_summary = "RequestError"
        expected_error_message = "TypeError while parsing request body: string indices must be integers."

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.parse_req_body(req_body=req_body)  # type: ignore # wrong type is the point of this test
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)


class TestValidateRequestsKeysAreAllowed(context.BaseTestCase):
    """Tests for validate_requests_keys_are_allowed function."""

    def test_validate_requests_keys_are_allowed_valid(self) -> None:
        """Test if validate_requests_keys_are_allowed does not raise an exception for valid keys."""
        operation = "insert"
        table_name = "test_table"
        allowed_operations = ["insert", "update", "delete"]
        allowed_table_names = ["test_table", "another_table"]

        # This should not raise an exception
        get_req_body.validate_requests_keys_are_allowed(
            operation=operation,
            table_name=table_name,
            allowed_operations=allowed_operations,
            allowed_table_names=allowed_table_names,
        )

    def test_validate_requests_keys_are_allowed_invalid_operation(self) -> None:
        """Test if validate_requests_keys_are_allowed raises TableOperationsError for invalid operation."""
        operation = "invalid_operation"
        table_name = "test_table"
        allowed_operations = ["insert", "update", "delete"]
        allowed_table_names = ["test_table", "another_table"]
        expected_error_summary = "RequestError"
        expected_error_message = f"Operation is not correct. Please choose one from '{allowed_operations}'."

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.validate_requests_keys_are_allowed(
                operation=operation,
                table_name=table_name,
                allowed_operations=allowed_operations,
                allowed_table_names=allowed_table_names,
            )
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)

    def test_validate_requests_keys_are_allowed_invalid_table_name(self) -> None:
        """Test if validate_requests_keys_are_allowed raises TableOperationsError for invalid table name."""
        operation = "insert"
        table_name = "invalid_table"
        allowed_operations = ["insert", "update", "delete"]
        allowed_table_names = ["test_table", "another_table"]
        expected_error_summary = "RequestError"
        expected_error_message = f"Table name is not correct. Please choose one from '{allowed_table_names}'."

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.validate_requests_keys_are_allowed(
                operation=operation,
                table_name=table_name,
                allowed_operations=allowed_operations,
                allowed_table_names=allowed_table_names,
            )
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)


class TestValidatePartitionAndRowKeysAreStrings(context.BaseTestCase):
    """Tests for validate_partition_and_row_keys_are_strings function."""

    def test_validate_partition_and_row_keys_are_strings_valid(self) -> None:
        """Test if validate_partition_and_row_keys_are_strings does not raise an exception for valid keys."""
        entity = {"PartitionKey": "part1", "RowKey": "row1", "other": 123}

        # This should not raise an exception
        get_req_body.validate_partition_and_row_keys_are_strings(entity=entity)

    def test_validate_partition_and_row_keys_are_strings_invalid(self) -> None:
        """Test if validate_partition_and_row_keys_are_strings raises TableOperationsError for invalid keys."""
        entity = {"PartitionKey": 123, "RowKey": "row1", "other": 123}
        expected_error_summary = "RequestError"
        expected_error_message = (
            "Value of PartitionKey (<class 'int'>) is not a string. Please check your request body."
        )

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.validate_partition_and_row_keys_are_strings(entity=entity)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)


class TestConvertNullsToEmptyString(context.BaseTestCase):  # pylint: disable=R0903:too-few-public-methods
    """Tests for convert_nulls_to_empty_string function."""

    def test_convert_nulls_to_empty_string(self) -> None:
        """Test if convert_nulls_to_empty_string correctly converts null values to empty strings."""
        entity = {"key1": "value1", "key2": None, "key3": "value3", "key4": None}

        result = get_req_body.convert_nulls_to_empty_string(entity=entity)

        self.assertEqual(first=result, second={"key1": "value1", "key2": "", "key3": "value3", "key4": ""})


class TestConvertDatetimeFields(context.BaseTestCase):
    """Tests for convert_datetime_fields function."""

    def test_convert_datetime_fields(self) -> None:
        """Test if convert_datetime_fields correctly converts datetime fields."""
        entity = {"date_from": "2022-01-01", "date_to": "2022-12-31", "other_field": "value"}
        datetime_fields = ["date_from", "date_to"]
        expected_result = {
            "date_from": datetime.datetime(year=2022, month=1, day=1, tzinfo=datetime.timezone.utc),
            "date_to": datetime.datetime(year=2022, month=12, day=31, tzinfo=datetime.timezone.utc),
            "other_field": "value",
        }

        result = get_req_body.convert_datetime_fields(entity=entity, datetime_fields=datetime_fields)

        self.assertEqual(first=result, second=expected_result)

    def test_convert_datetime_fields_invalid_date(self) -> None:
        """Test if convert_datetime_fields raises TableOperationsError for invalid date."""
        entity = {"date_from": "invalid_date", "date_to": "2022-12-31"}
        datetime_fields = ["date_from", "date_to"]
        expected_error_summary = "RequestError"
        expected_error_message = (
            "Error while parsing date_from date (invalid_date). Please provide date in format 'YYYY-MM-DD'."
        )

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.convert_datetime_fields(entity=entity, datetime_fields=datetime_fields)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)


class TestMain(context.BaseTestCase):  # pylint: disable=R0903:too-few-public-methods
    """Tests for main function."""

    @patch("modules.get_req_body.req_to_json")
    @patch("modules.get_req_body.parse_req_body")
    @patch("modules.get_req_body.validate_requests_keys_are_allowed")
    @patch("modules.get_req_body.validate_partition_and_row_keys_are_strings")
    @patch("modules.get_req_body.convert_nulls_to_empty_string")
    @patch("modules.get_req_body.convert_datetime_fields")
    def test_main(  # pylint: disable=R0913:too-many-arguments
        self,
        mock_convert_datetime_fields,
        mock_convert_nulls_to_empty_string,
        mock_validate_partition_and_row_keys_are_strings,
        mock_validate_requests_keys_are_allowed,
        mock_parse_req_body,
        mock_req_to_json,
    ) -> None:
        """Test if main correctly processes a valid request."""
        mock_req = MagicMock()
        mock_req_to_json.return_value = {"entity": {"key": "value"}, "table_name": "test_table", "operation": "insert"}
        mock_parse_req_body.return_value = ({"key": "value"}, "test_table", "insert")
        mock_convert_nulls_to_empty_string.return_value = {"key": "value"}
        mock_convert_datetime_fields.return_value = {"key": "value"}

        result = get_req_body.main(
            req=mock_req,
            allowed_table_names=["test_table"],
            allowed_operations=["insert"],
            datetime_fields=["date_from", "date_to"],
        )

        self.assertEqual(first=result, second=({"key": "value"}, "test_table", "insert"))

        mock_req_to_json.assert_called_once_with(req=mock_req)
        mock_parse_req_body.assert_called_once_with(req_body=mock_req_to_json.return_value)
        mock_validate_requests_keys_are_allowed.assert_called_once_with(
            operation="insert",
            table_name="test_table",
            allowed_operations=["insert"],
            allowed_table_names=["test_table"],
        )
        mock_validate_partition_and_row_keys_are_strings.assert_called_once_with(entity={"key": "value"})
        mock_convert_nulls_to_empty_string.assert_called_once_with(entity={"key": "value"})


if __name__ == "__main__":
    unittest.main()
