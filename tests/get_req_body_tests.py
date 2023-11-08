"""Unit tests for modules.get_req_body_tests"""
import datetime
import unittest
from unittest.mock import Mock, patch, MagicMock

import azure.functions


import context  # pylint: disable=E0401:import-error
from modules import custom_error, get_req_body


class GetReqBodyBaseTestCase(context.BaseTestCase):
    """Base class for entity operations module tests.
    Sets up mock TableClient object and expected exception for all tests.
    Sets side effect for mock_table_client.query_entities method to None before each test.
    """

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=C0103:invalid-name
        """Extends setUpClass method from context.BaseTestCase.
        Sets up mock TableClient object and expected exception for all tests."""
        super().setUpClass()
        cls.valid_entity = {"key": "value"}
        cls.valid_operation = "insert"
        cls.valid_table_name = "test_table"
        cls.req_body = {
            "entity": cls.valid_entity,
            "table_name": cls.valid_table_name,
            "operation": cls.valid_operation,
        }
        cls.parsed_body_tuple = (cls.valid_entity, cls.valid_table_name, cls.valid_operation)


class TestReqToJson(GetReqBodyBaseTestCase):
    """Tests for req_to_json function."""

    def test_req_to_json_valid(self) -> None:
        """Test if req_to_json returns valid JSON."""
        mock_request = Mock(spec=azure.functions.HttpRequest)
        mock_request.get_json.return_value = self.valid_entity
        expected_result = self.valid_entity

        result = get_req_body.req_to_json(req=mock_request)

        self.assertEqual(first=result, second=expected_result)

    def test_req_to_json_invalid(self) -> None:
        """Test if req_to_json raises TableOperationsError when request does not contain valid JSON data."""
        mock_request = Mock(spec=azure.functions.HttpRequest)
        mock_request.get_json.side_effect = ValueError("Invalid JSON")
        expected_error_summary = context.ERROR_REQUEST_ERROR

        with self.assertRaises(expected_exception=context.EXPECTED_EXCEPTION) as cm:
            get_req_body.req_to_json(req=mock_request)
            self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestParseReqBody(GetReqBodyBaseTestCase):
    """Tests for parse_req_body function."""

    def test_parse_req_body_valid(self) -> None:
        """Test if parse_req_body returns valid tuple."""
        expected_result = self.parsed_body_tuple

        result = get_req_body.parse_req_body(req_body=self.req_body)

        self.assertEqual(first=result, second=expected_result)

    def test_parse_req_body_key_error(self) -> None:
        """Test if parse_req_body raises TableOperationsError when request does not contain valid JSON data."""
        invalid_req_body = self.req_body.copy().pop("entity")
        expected_error_summary = context.ERROR_REQUEST_ERROR

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.parse_req_body(req_body=invalid_req_body)
            self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_parse_req_body_type_error(self) -> None:
        """Test if parse_req_body raises TableOperationsError when request does not contain valid JSON data."""
        invalid_req_body = "not a dictionary"
        expected_error_summary = context.ERROR_REQUEST_ERROR

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.parse_req_body(req_body=invalid_req_body)
            self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestValidateRequestsKeysAreAllowed(GetReqBodyBaseTestCase):
    """Tests for validate_requests_keys_are_allowed function."""

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=C0103:invalid-name
        """Extends setUpClass method from GetReqBodyBaseTestCase with repeatable constants."""
        super().setUpClass()
        cls.allowed_operations = ["insert", "update", "delete"]
        cls.allowed_table_names = ["test_table", "another_table"]

    def test_validate_requests_keys_are_allowed_valid(self) -> None:
        """Test if validate_requests_keys_are_allowed does not raise an exception for valid keys."""
        # This should not raise an exception
        get_req_body.validate_requests_keys_are_allowed(
            operation=self.valid_operation,
            table_name=self.valid_table_name,
            allowed_operations=self.allowed_operations,
            allowed_table_names=self.allowed_table_names,
        )

    def test_validate_requests_keys_are_allowed_invalid_operation(self) -> None:
        """Test if validate_requests_keys_are_allowed raises TableOperationsError for invalid operation."""
        invalid_operation = "invalid_operation"
        expected_error_summary = context.ERROR_REQUEST_ERROR

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.validate_requests_keys_are_allowed(
                operation=invalid_operation,
                table_name=self.valid_table_name,
                allowed_operations=self.allowed_operations,
                allowed_table_names=self.allowed_table_names,
            )
            self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_validate_requests_keys_are_allowed_invalid_table_name(self) -> None:
        """Test if validate_requests_keys_are_allowed raises TableOperationsError for invalid table name."""
        invalid_table_name = "invalid_table"
        expected_error_summary = context.ERROR_REQUEST_ERROR

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.validate_requests_keys_are_allowed(
                operation=self.valid_operation,
                table_name=invalid_table_name,
                allowed_operations=self.allowed_operations,
                allowed_table_names=self.allowed_table_names,
            )
            self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestValidatePartitionAndRowKeysAreStrings(GetReqBodyBaseTestCase):
    """Tests for validate_partition_and_row_keys_are_strings function."""

    def test_validate_partition_and_row_keys_are_strings_valid(self) -> None:
        """Test if validate_partition_and_row_keys_are_strings does not raise an exception for valid keys."""
        valid_entity = {"PartitionKey": "part1", "RowKey": "row1", "other": 123}

        # This should not raise an exception
        get_req_body.validate_partition_and_row_keys_are_strings(entity=valid_entity)

    def test_validate_partition_and_row_keys_are_strings_invalid(self) -> None:
        """Test if validate_partition_and_row_keys_are_strings raises TableOperationsError for invalid keys."""
        invalid_entity = {"PartitionKey": 123, "RowKey": "row1", "other": 123}
        expected_error_summary = context.ERROR_REQUEST_ERROR

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.validate_partition_and_row_keys_are_strings(entity=invalid_entity)
            self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestConvertNullsToEmptyString(GetReqBodyBaseTestCase):  # pylint: disable=R0903:too-few-public-methods
    """Tests for convert_nulls_to_empty_string function."""

    def test_convert_nulls_to_empty_string(self) -> None:
        """Test if convert_nulls_to_empty_string correctly converts null values to empty strings."""
        entity = {"key1": "value1", "key2": None, "key3": "value3", "key4": None}
        expected_result = {"key1": "value1", "key2": "", "key3": "value3", "key4": ""}

        result = get_req_body.convert_nulls_to_empty_string(entity=entity)

        self.assertEqual(first=result, second=expected_result)


class TestConvertDatetime(GetReqBodyBaseTestCase):
    """Tests for convert_datetime function."""

    def test_convert_datetime_valid(self) -> None:
        """Test if convert_datetime correctly converts a valid date string."""
        date_string = "2022-01-01"
        expected_result = datetime.datetime(year=2022, month=1, day=1, tzinfo=datetime.timezone.utc)

        result = get_req_body.convert_datetime(date_string=date_string)

        self.assertEqual(first=result, second=expected_result)

    def test_convert_datetime_invalid(self) -> None:
        """Test if convert_datetime raises TableOperationsError for an invalid date string."""
        date_string = "invalid date string"
        expected_error_summary = context.ERROR_REQUEST_ERROR

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            get_req_body.convert_datetime(date_string=date_string)
            self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestMain(GetReqBodyBaseTestCase):  # pylint: disable=R0903:too-few-public-methods
    """Tests for main function."""

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=C0103:invalid-name
        """Extends setUpClass method from GetReqBodyBaseTestCase with repeatable constants."""
        super().setUpClass()
        cls.allowed_operations = ["insert", "update", "delete"]
        cls.allowed_table_names = ["test_table", "another_table"]

    @patch("modules.get_req_body.req_to_json")
    @patch("modules.get_req_body.parse_req_body")
    @patch("modules.get_req_body.validate_requests_keys_are_allowed")
    @patch("modules.get_req_body.validate_partition_and_row_keys_are_strings")
    @patch("modules.get_req_body.convert_nulls_to_empty_string")
    @patch("modules.get_req_body.convert_datetime")
    def test_main(  # pylint: disable=R0903:too-few-public-methods
        self,
        mock_convert_datetime,
        mock_convert_nulls_to_empty_string,
        mock_validate_partition_and_row_keys_are_strings,
        mock_validate_requests_keys_are_allowed,
        mock_parse_req_body,
        mock_req_to_json,
    ) -> None:
        """Test if main correctly processes a valid request."""
        mock_req = MagicMock()
        mock_req_to_json.return_value = self.req_body
        mock_parse_req_body.return_value = self.parsed_body_tuple
        mock_convert_nulls_to_empty_string.return_value = self.valid_entity
        mock_convert_datetime.return_value = "2022-01-01"
        expected_result = self.parsed_body_tuple

        result = get_req_body.main(
            req=mock_req, allowed_table_names=self.allowed_table_names, allowed_operations=self.allowed_operations
        )

        self.assertEqual(first=result, second=expected_result)

        mock_req_to_json.assert_called_once_with(req=mock_req)
        mock_parse_req_body.assert_called_once_with(req_body=mock_req_to_json.return_value)
        mock_validate_requests_keys_are_allowed.assert_called_once_with(
            operation=self.valid_operation,
            table_name=self.valid_table_name,
            allowed_operations=self.allowed_operations,
            allowed_table_names=self.allowed_table_names,
        )
        mock_validate_partition_and_row_keys_are_strings.assert_called_once_with(entity=self.valid_entity)
        mock_convert_nulls_to_empty_string.assert_called_once_with(entity=self.valid_entity)


if __name__ == "__main__":
    unittest.main()
