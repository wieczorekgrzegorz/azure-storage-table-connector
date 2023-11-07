"""Unit tests for modules.main"""
import unittest
from unittest.mock import Mock, patch, MagicMock

import azure.functions
from azure.data.tables import TableServiceClient, TableClient, _deserialize


import context  # pylint: disable=E0401:import-error
from modules import main, custom_error, entity_operations


class TestCreateTableService(context.BaseTestCase):  # pylint: disable=R0904:too-few-public-methods
    """Tests for entity_operations.create_table_service function."""

    @patch(target="modules.main.TableServiceClient", autospec=True)
    def test_function_returns_table_service_client(self, mock_table_service_client) -> None:
        """Test if function returns TableServiceClient object."""
        connection_string = "connection_string"
        mock_client = Mock(spec=TableServiceClient)
        mock_table_service_client.from_connection_string.return_value = mock_client

        result = main.create_table_service(connection_string=connection_string)
        self.assertIsInstance(obj=result, cls=TableServiceClient)


class TestCreateTableClient(context.BaseTestCase):  # pylint: disable=R0904:too-few-public-methods
    """Tests for entity_operations.create_table_client function."""

    @patch(target="modules.main.TableServiceClient", autospec=True)
    def test_function_returns_table_client(self, mock_table_service_client) -> None:
        """Test if function returns TableClient object."""
        mock_table_client = Mock(spec=TableClient)
        mock_table_service_client.get_table_client.return_value = mock_table_client
        table_name = "table_name"

        result = main.create_table_client(
            table_service_client=mock_table_service_client,
            table_name=table_name,
        )
        self.assertIsInstance(obj=result, cls=TableClient)


class TestBuildErrorDict(context.BaseTestCase):  # pylint: disable=R0904:too-few-public-methods
    """Tests for entity_operations.build_error_dict function."""

    def test_function_returns_error_dict(self) -> None:
        """Test if function returns error dictionary."""
        error = custom_error.TableOperationsError(
            summary="summary",
            message="message",
        )
        expected_result = {
            "error": error.summary,
            "message": error.message,
        }

        result = main.build_error_dict(e=error)
        self.assertEqual(first=result, second=expected_result)


class TestBuildHTTPResponse(context.BaseTestCase):  # pylint: disable=R0904:too-few-public-methods
    """Tests for entity_operations.build_http_response function."""

    def test_function_returns_http_response(self) -> None:
        """Test if function returns func.HttpResponse object."""
        response_dict = {"response": "response"}

        result = main.build_http_response(response_dict=response_dict)
        self.assertIsInstance(obj=result, cls=azure.functions.HttpResponse)

    def test_function_raises_error(self) -> None:
        """Test if function raises TableOperationsError when response_dict is not JSON-serializable."""
        response_dict = {"response": "response"}
        type_error_message = "Test error message."
        side_effect = TypeError(type_error_message)

        expected_error_message = f"Error while building HTTP response: {type_error_message}."
        expected_error_summary = "TypeError"

        with patch(target="modules.main.json.dumps", side_effect=side_effect):
            with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
                main.build_http_response(response_dict=response_dict)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)


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
        expected_result = [{"PartitionKey": "test", "RowKey": "test", "Timestamp": str(datetime_obj)} for _ in range(3)]

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


class TestMain(context.BaseTestCase):
    """Tests for main.main function."""

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=C0103:invalid-name
        """Sets up variables used in all tests."""
        cls.req = MagicMock()
        cls.connection_string = (
            "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey;EndpointSuffix=core.windows.net"
        )
        cls.allowed_table_names = ["test_table"]
        cls.allowed_operations = ["get"]

    def setUp(self) -> None:  # pylint: disable=C0103:invalid-name
        """Sets up mocks for all tests."""
        super().setUp()
        self.mock_get_req_body_main = patch("modules.main.get_req_body.main").start()
        self.mock_create_table_client = patch("modules.main.create_table_client").start()
        self.mock_query_table = patch("modules.main.query_table").start()
        self.mock_datetime_to_string = patch("modules.main.convert_tables_entity_datetime_to_string").start()
        self.mock_build_http_response = patch("modules.main.build_http_response").start()

    def tearDown(self) -> None:  # pylint: disable=C0103:invalid-name
        """Teardown mocks for all tests."""
        patch("modules.main.get_req_body.main").stop()
        patch("modules.main.create_table_client").stop()
        patch("modules.main.query_table").stop()
        patch("modules.main.convert_tables_entity_datetime_to_string").stop()
        patch("modules.main.build_http_response").stop()
        super().tearDown()

    def test_successfull_main_execution(self) -> None:
        """Test for case when main.main executes successfully."""
        mock_http_response = Mock(spec=azure.functions.HttpResponse)
        expected_result = mock_http_response

        self.mock_get_req_body_main.return_value = ({"PartitionKey": "test", "RowKey": "test"}, "test", "test")
        self.mock_create_table_client.return_value = Mock(spec=TableClient)
        self.mock_query_table.return_value = {"response": "response"}
        self.mock_datetime_to_string.return_value = {"response": "response"}
        self.mock_build_http_response.return_value = mock_http_response

        test_result = main.main(
            req=self.req,
            connection_string=self.connection_string,
            allowed_table_names=self.allowed_table_names,
            allowed_operations=self.allowed_operations,
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
        mock_return_value = azure.functions.HttpResponse(body=expected_result)

        self.mock_get_req_body_main.side_effect = side_effect
        self.mock_get_req_body_main.return_value = None
        self.mock_build_http_response.return_value = mock_return_value

        test_result_http_response = main.main(
            req=self.req,
            connection_string=self.connection_string,
            allowed_table_names=self.allowed_table_names,
            allowed_operations=self.allowed_operations,
        )

        test_result = test_result_http_response.get_body()

        self.assertEqual(first=test_result, second=expected_result)
        self.mock_create_table_client.assert_not_called()
        self.mock_query_table.assert_not_called()
        self.mock_datetime_to_string.assert_not_called()
        self.mock_build_http_response.assert_called_once_with(response_dict=mock_return_body_dict)

    def test_main_handling_unexpected_error(self) -> None:
        """Test for case when main.main raises unexpected error.
        In this case, main.main should return HTTP response with error details in body."""
        side_effect = TypeError("test_message")
        expected_result = b'{"query_result": null, "error": {"error": "TypeError", "message": "test_message"}}'

        mock_return_body_dict = {"query_result": None, "error": {"error": "TypeError", "message": "test_message"}}
        mock_return_value = azure.functions.HttpResponse(body=expected_result)

        self.mock_get_req_body_main.side_effect = side_effect
        self.mock_get_req_body_main.return_value = None
        self.mock_build_http_response.return_value = mock_return_value

        test_result_http_response = main.main(
            req=self.req,
            connection_string=self.connection_string,
            allowed_table_names=self.allowed_table_names,
            allowed_operations=self.allowed_operations,
        )

        test_result = test_result_http_response.get_body()

        self.assertEqual(first=test_result, second=expected_result)
        self.mock_create_table_client.assert_not_called()
        self.mock_query_table.assert_not_called()
        self.mock_datetime_to_string.assert_not_called()
        self.mock_build_http_response.assert_called_once_with(response_dict=mock_return_body_dict)


if __name__ == "__main__":
    unittest.main()
