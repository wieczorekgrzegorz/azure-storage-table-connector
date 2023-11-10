"""Unit tests for modules.main.py"""
import unittest
from unittest.mock import Mock, patch, MagicMock

import azure.functions as func
from azure.data.tables import _deserialize

from modules import main, entity_operations
from modules.main import TableClient
from modules.utilities import custom_error
from . import context


class TestBuildHTTPResponse(context.BaseTestCase):
    """Tests for build_http_response function."""

    def test_build_http_response(self) -> None:
        """Test valid input for build_http_response function."""
        response_dict = {"key": "value"}
        expected_http_response = func.HttpResponse(body='{"key": "value"}')

        http_response = main.build_http_response(response_dict=response_dict)

        self.assertEqual(first=http_response.get_body(), second=expected_http_response.get_body())

    def test_build_http_response_error(self) -> None:
        """Test error for build_http_response function."""
        response_dict = {"key": set()}  # sets are not JSON-serializable

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            main.build_http_response(response_dict=response_dict)

        self.assertEqual(first=cm.exception.summary, second="TypeError")
        self.assertTrue(expr="is not JSON serializable" in cm.exception.message)


class TestQueryTable(context.BaseTestCase):  # pylint: disable=R0904:too-few-public-methods
    """Tests for main.query_table function."""

    def test_successfull_get_operation(self) -> None:
        """Test for case when query_table operation is successful."""
        mock_table_client = Mock(spec=TableClient)
        operation = "get"
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_result = {"response": "response"}

        entity_operations.get = MagicMock(return_value=expected_result)

        test_result = main.query_table(operation=operation, table_client=mock_table_client, entity=entity)

        self.assertEqual(first=test_result, second=expected_result)


class TestConvertTablesEntityDatetimeToString(context.BaseTestCase):
    """Tests for main.convert_tables_entity_datetime_to_string function."""

    def test_convert_single_dict(self) -> None:
        """Test for case when query_result is a single dictionary."""
        datetime_obj = _deserialize.TablesEntityDatetime(year=1970, month=1, day=1)
        query_result = {"PartitionKey": "test", "RowKey": "test", "Timestamp": datetime_obj}
        expected_result = {"PartitionKey": "test", "RowKey": "test", "Timestamp": str(object=datetime_obj)}

        test_result = main.convert_tables_entity_datetime_to_string(query_result=query_result)

        self.assertEqual(first=test_result, second=expected_result)

    def test_convert_list_of_dicts(self) -> None:
        """Test for case when query_result is a list of dictionaries."""
        datetime_obj = _deserialize.TablesEntityDatetime(year=1970, month=1, day=1)
        query_result = [{"PartitionKey": "test", "RowKey": "test", "Timestamp": datetime_obj} for _ in range(3)]
        expected_result = [
            {"PartitionKey": "test", "RowKey": "test", "Timestamp": str(object=datetime_obj)} for _ in range(3)
        ]

        test_result = main.convert_tables_entity_datetime_to_string(query_result=query_result)

        self.assertEqual(first=test_result, second=expected_result)

    def test_convert_empty_dict(self) -> None:
        """Test for case when query_result is an empty dictionary."""
        query_result = {}
        expected_result = {}

        test_result = main.convert_tables_entity_datetime_to_string(query_result=query_result)

        self.assertEqual(first=test_result, second=expected_result)

    def test_convert_empty_list(self) -> None:
        """Test for case when query_result is an empty list."""
        query_result = []
        expected_result = []

        test_result = main.convert_tables_entity_datetime_to_string(query_result=query_result)

        self.assertEqual(first=test_result, second=expected_result)


class TestMainMain(context.BaseTestCase):
    """Tests for main.main function."""

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=C0103:invalid-name
        """Sets up variables used in all tests."""
        super().setUpClass()
        cls.req = MagicMock()
        cls.connection_string = (
            "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"
        )
        cls.allowed_table_names = ["test_table"]
        cls.allowed_operations = ["get"]
        cls.datetime_fields = ["Timestamp"]
        cls.mock_table_service_client = MagicMock(spec=main.TableServiceClient)
        cls.mock_table_client = MagicMock(spec=main.TableClient)

    def setUp(self) -> None:  # pylint: disable=C0103:invalid-name
        """Sets up mocks for all tests."""
        super().setUp()
        self.mock_get_req_body_main = patch("modules.main.get_req_body.main").start()
        self.mock_query_table = patch("modules.main.query_table").start()
        self.mock_datetime_to_string = patch("modules.main.convert_tables_entity_datetime_to_string").start()
        self.mock_build_http_response = patch("modules.main.build_http_response").start()

    def tearDown(self) -> None:  # pylint: disable=C0103:invalid-name
        """Teardown mocks for all tests."""
        patch("modules.main.get_req_body.main").stop()
        patch("modules.main.query_table").stop()
        patch("modules.main.convert_tables_entity_datetime_to_string").stop()
        patch("modules.main.build_http_response").stop()
        super().tearDown()

    def test_successfull_main_execution(self) -> None:
        """Test for case when main.main executes successfully."""
        mock_http_response = Mock(spec=func.HttpResponse)
        expected_result = mock_http_response

        self.mock_get_req_body_main.return_value = ({"PartitionKey": "test", "RowKey": "test"}, "test", "test")
        self.mock_table_service_client.from_connection_string.return_value = self.mock_table_service_client

        self.mock_table_service_client.get_table_client.return_value = self.mock_table_client

        self.mock_query_table.return_value = {"response": "response"}
        self.mock_datetime_to_string.return_value = {"response": "response"}
        self.mock_build_http_response.return_value = mock_http_response

        test_result = main.main(
            req=self.req,
            connection_string=self.connection_string,
            allowed_table_names=self.allowed_table_names,
            allowed_operations=self.allowed_operations,
            datetime_fields=self.datetime_fields,
        )

        self.assertEqual(first=test_result, second=expected_result)

    def test_main_handling_table_operations_error(self) -> None:
        """Test for case when main.main raises TableOperationsError.
        In this case, main.main should return HTTP response with error details in body."""

        side_effect = custom_error.TableOperationsError(
            summary="summary",
            message="message",
        )
        expected_result = b'{"query_result": null, "error": {"error": "summary", "message": "message"}}'
        mock_return_body_dict = {"query_result": None, "error": {"error": "summary", "message": "message"}}
        mock_return_value = func.HttpResponse(body=expected_result)

        self.mock_get_req_body_main.side_effect = side_effect
        self.mock_get_req_body_main.return_value = None
        self.mock_build_http_response.return_value = mock_return_value

        test_result_http_response = main.main(
            req=self.req,
            connection_string=self.connection_string,
            allowed_table_names=self.allowed_table_names,
            allowed_operations=self.allowed_operations,
            datetime_fields=self.datetime_fields,
        )

        test_result = test_result_http_response.get_body()

        self.assertEqual(first=test_result, second=expected_result)
        self.mock_query_table.assert_not_called()
        self.mock_datetime_to_string.assert_not_called()
        self.mock_build_http_response.assert_called_once_with(response_dict=mock_return_body_dict)

    def test_main_handling_unexpected_error(self) -> None:
        """Test for case when main.main raises unexpected error.
        In this case, main.main should return HTTP response with error details in body."""
        side_effect = TypeError("test_message")
        expected_result = b'{"query_result": null, "error": {"error": "TypeError", "message": "test_message"}}'

        mock_return_body_dict = {"query_result": None, "error": {"error": "TypeError", "message": "test_message"}}
        mock_return_value = func.HttpResponse(body=expected_result)

        self.mock_get_req_body_main.side_effect = side_effect
        self.mock_get_req_body_main.return_value = None
        self.mock_build_http_response.return_value = mock_return_value

        test_result_http_response = main.main(
            req=self.req,
            connection_string=self.connection_string,
            allowed_table_names=self.allowed_table_names,
            allowed_operations=self.allowed_operations,
            datetime_fields=self.datetime_fields,
        )

        test_result = test_result_http_response.get_body()

        self.assertEqual(first=test_result, second=expected_result)
        self.mock_query_table.assert_not_called()
        self.mock_datetime_to_string.assert_not_called()
        self.mock_build_http_response.assert_called_once_with(response_dict=mock_return_body_dict)


if __name__ == "__main__":
    unittest.main()
