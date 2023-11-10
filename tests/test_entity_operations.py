"""Unit tests for entity_operations.py"""
import unittest
from unittest.mock import Mock, patch, MagicMock

import azure.core.exceptions as azure_exceptions

import context  # pylint: disable=E0401:import-error
from modules import entity_operations
from modules.utilities import custom_error


class BaseEntityOperationsTest(context.BaseTestCase):
    """Base class for entity_operations.py tests, sets up common mock objects and patches."""

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=C0103:invalid-name
        """Mocks TableClient for all entity_operations.py test sub-classes."""
        super().setUpClass()
        cls.mock_table_client = Mock(spec=entity_operations.TableClient)

    def setUp(self) -> None:  # pylint: disable=C0103:invalid-name
        """Resets mock_table_client side efect before each test."""
        super().setUp()
        self.mock_table_client.query_entities.side_effect = None


class TestGet(BaseEntityOperationsTest):
    """Tests for get function."""

    def test_get(self) -> None:
        """Test valid input for get function."""
        self.mock_table_client.query_entities.return_value = [{"PartitionKey": "key1", "RowKey": "row1"}]
        entity = {"PartitionKey": "key1", "RowKey": "row1"}
        expected_result = {"PartitionKey": "key1", "RowKey": "row1"}

        result = entity_operations.get(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=result, second=expected_result)

    def test_get_no_entity(self) -> None:
        """Test no entity found for get function."""
        self.mock_table_client.query_entities.return_value = []
        entity = {"PartitionKey": "key1", "RowKey": "row1"}

        expected_error_summary = "NoEntity"
        expected_error_message = f"No entities found for {entity['PartitionKey']}/{entity['RowKey']}."

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            entity_operations.get(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_get_multiple_entities(self) -> None:
        """Test multiple entities found for get function."""
        self.mock_table_client.query_entities.return_value = [
            {"PartitionKey": "key1", "RowKey": "row1"},
            {"PartitionKey": "key1", "RowKey": "row1"},
        ]
        entity = {"PartitionKey": "key1", "RowKey": "row1"}

        expected_error_summary = "MoreThanOneEntityFound"
        expected_error_message = f"More than one entity found for PartitionKey '{entity['PartitionKey']}'/\
                and RowKey '{entity['RowKey']}"

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            entity_operations.get(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_get_azure_error(self) -> None:
        """Test AzureError for get function."""
        self.mock_table_client.query_entities.side_effect = azure_exceptions.HttpResponseError(message="Test Error")
        entity = {"PartitionKey": "key1", "RowKey": "row1"}

        expected_error_summary = "AzureError"
        expected_error_message = "Test Error"

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            entity_operations.get(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestGetAll(BaseEntityOperationsTest):
    """Tests for get_all function."""

    def test_get_all(self) -> None:
        """Test valid input for get_all function."""
        entity = {"PartitionKey": "key1", "RowKey": "row1"}
        self.mock_table_client.query_entities.return_value = [entity]
        expected_result = [entity]

        result = entity_operations.get_all(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=result, second=expected_result)

    def test_get_all_no_entity(self) -> None:
        """Test no entity found for get_all function."""
        self.mock_table_client.query_entities.return_value = []
        entity = {"PartitionKey": "key1", "RowKey": "row1"}

        expected_error_summary = "NoEntity"
        expected_error_message = f"No entities found for {entity}."

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            entity_operations.get_all(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_get_all_azure_error(self) -> None:
        """Test AzureError for get_all function."""
        self.mock_table_client.query_entities.side_effect = azure_exceptions.HttpResponseError(message="Test Error")
        entity = {"PartitionKey": "key1", "RowKey": "row1"}

        expected_error_summary = "AzureError"
        expected_error_message = "Test Error"

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            entity_operations.get_all(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_get_all_missing_keys(self) -> None:
        """Test RequiredKeyMissing for get_all function."""
        entity = {}

        expected_error_summary = "RequiredKeyMissing"
        expected_error_message = "Both 'PartitionKey' and 'RowKey' are missing from entity: {}. Provide at least one."

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            entity_operations.get_all(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestDelete(BaseEntityOperationsTest):
    """Tests for delete function."""

    def test_delete(self) -> None:
        """Test valid input for delete function: table_client.get_entity returning ResourceNotFoundError"""
        entity = {"PartitionKey": "key1", "RowKey": "row1"}
        expected_result = {"response": "Entity 'key1/row1' removed from table."}

        self.mock_table_client.get_entity.side_effect = azure_exceptions.ResourceNotFoundError(message="Not found")

        result = entity_operations.delete(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=result, second=expected_result)

    def test_delete_not_removed(self) -> None:
        """Test entity not removed for delete function: table_client.get_entity not returning ResourceNotFoundError."""
        entity = {"PartitionKey": "key1", "RowKey": "row1"}
        self.mock_table_client.get_entity.side_effect = None

        expected_error_summary = "AzureError"
        expected_error_message = "Entity 'key1/row1' NOT removed from table."

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            entity_operations.delete(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestValidateResult(BaseEntityOperationsTest):
    """Tests for validate_result function."""

    def test_validate_result_no_discrepancy(self) -> None:
        """Test valid input for validate_result function with no discrepancy."""
        entity = {"PartitionKey": "key1", "RowKey": "row1", "other_field": "value"}
        self.mock_table_client.get_entity.return_value = entity

        # No exception should be raised
        entity_operations.validate_result(table_client=self.mock_table_client, entity=entity)

    def test_validate_result_discrepancy_found(self) -> None:
        """Test discrepancy found for validate_result function."""
        entity = {"PartitionKey": "key1", "RowKey": "row1", "other_field": "value"}
        self.mock_table_client.get_entity.return_value = {
            "PartitionKey": "key1",
            "RowKey": "row1",
            "other_field": "different_value",
        }

        expected_error_summary = "EntityOperationFailed"
        expected_error_message = (
            f"Entity in table: {self.mock_table_client.get_entity.return_value}, entity to be inserted: {entity}."
        )

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            entity_operations.validate_result(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestUpdate(BaseEntityOperationsTest):
    """Tests for update function."""

    @patch("module_where_validate_result_is_defined.validate_result")
    def test_update(self, mock_validate_result) -> None:
        """Test valid input for update function."""
        entity = {"PartitionKey": "key1", "RowKey": "row1", "other_field": "value"}
        expected_result = {"response": "Entity 'key1/row1' updated."}

        self.mock_table_client.update_entity.return_value = None

        result = entity_operations.update(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=result, second=expected_result)
        mock_validate_result.assert_called_once_with(table_client=self.mock_table_client, entity=entity)

    @patch("module_where_validate_result_is_defined.validate_result")
    def test_update_error(self, mock_validate_result) -> None:
        """Test error for update function."""
        entity = {"PartitionKey": "key1", "RowKey": "row1", "other_field": "value"}

        expected_error_summary = "AzureError"
        expected_error_message = "Some error message"

        self.mock_table_client.update_entity.side_effect = azure_exceptions.HttpResponseError(
            message=expected_error_message
        )

        with self.assertRaises(expected_exception=custom_error.TableOperationsError) as cm:
            entity_operations.update(table_client=self.mock_table_client, entity=entity)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)
        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        mock_validate_result.assert_not_called()


if __name__ == "__main__":
    unittest.main()

# TODO [KK-190]  Storage Table Connector: add tests for enitity_operations.py
