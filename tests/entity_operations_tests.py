"""Unit tests for modules.entity_operations"""
import unittest
from unittest.mock import patch, MagicMock

from azure.data.tables import TableClient
import azure.core.exceptions as azure_exceptions

import context  # pylint: disable=E0401:import-error
from modules import custom_error, entity_operations


class EntityOperationBaseTestCase(context.BaseTestCase):
    """Base class for entity operations module tests.
    Sets up mock TableClient object and expected exception for all tests.
    Sets side effect for mock_table_client.query_entities method to None before each test.
    """

    @classmethod
    def setUpClass(cls) -> None:  # pylint: disable=C0103:invalid-name
        """Extension of setUpClass method from context.BaseTestCase.
        Sets up mock TableClient object and expected exception for all tests."""
        super().setUpClass()
        cls.mock_table_client = MagicMock(spec=TableClient)
        cls.expected_exception = custom_error.TableOperationsError

    def setUp(self) -> None:  # pylint: disable=C0103:invalid-name
        """Extension of setUp method from context.BaseTestCase.
        Sets side effect for mock_table_client.query_entities method to None before each test."""
        super().setUp()
        self.mock_table_client.query_entities.side_effect = None
        self.mock_table_client.delete_entity.side_effect = None
        self.mock_table_client.get_entity.side_effect = None


class TestGet(EntityOperationBaseTestCase):
    """Tests for entity_operations.get function."""

    def test_successfull_path(self) -> None:
        """Test for case when exactly one entity (list with one item) is found for specified PartitionKey and RowKey."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_result = entity

        self.mock_table_client.query_entities.return_value = [entity]

        test_result = entity_operations.get(table_client=self.mock_table_client, entity=entity)

        self.assertIsInstance(obj=test_result, cls=dict)
        self.assertEqual(first=test_result, second=expected_result)

    def test_raises_error_if_resource_not_found_error(self) -> None:
        """Test for case when ResourceNotFoundError is raised by query_entities method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.query_entities.side_effect = azure_exceptions.HttpResponseError()
        self.mock_table_client.query_entities.return_value = None

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.get(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_raises_error_if_http_response_error(self) -> None:
        """Test for case when HttpResponseError is raised by query_entities method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.query_entities.side_effect = azure_exceptions.ResourceNotFoundError()
        self.mock_table_client.query_entities.return_value = None

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.get(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_raises_error_if_no_records_found(self) -> None:
        """Test for case when no entities are found for specified PartitionKey and RowKey
        (== table_client.query_entities returns empty list)."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "NoEntity"

        self.mock_table_client.query_entities.return_value = []

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.get(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_raises_error_if_more_records_found(self) -> None:
        """Test for case when more than one entity is found for specified PartitionKey and RowKey."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "MoreThanOneEntityFound"

        self.mock_table_client.query_entities.return_value = [entity, entity]

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.get(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestGetAll(EntityOperationBaseTestCase):
    """Tests for entity_operations.get_all function."""

    def test_successfull_path(self) -> None:
        """Tests for case when table query for entities with specified RowKey returns a list of entities."""
        entity = {"RowKey": "test"}
        expected_result = [entity, entity]

        self.mock_table_client.query_entities.return_value = [entity, entity]

        test_result = entity_operations.get_all(table_client=self.mock_table_client, entity=entity)

        self.assertIsInstance(obj=test_result, cls=list)
        self.assertEqual(first=test_result, second=expected_result)

    def test_raises_error_if_resource_not_found_error(self) -> None:
        """Test for case when ResourceNotFoundError is raised by query_entities method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.query_entities.side_effect = azure_exceptions.ResourceNotFoundError()
        self.mock_table_client.query_entities.return_value = None

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.get_all(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_raises_error_if_http_response_error(self) -> None:
        """Test for case when HttpResponseError is raised by query_entities method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.query_entities.side_effect = azure_exceptions.HttpResponseError()
        self.mock_table_client.query_entities.return_value = None

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.get_all(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)

    def test_raises_error_if_no_records_found(self) -> None:
        """Test for case when table query returns an empty list:
        no entities are found for specified PartitionKey and RowKey."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "NoEntity"

        self.mock_table_client.query_entities.return_value = []

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.get_all(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)


class TestDelete(EntityOperationBaseTestCase):
    """Tests for entity_operations.delete function."""

    def test_successfull_path(self) -> None:
        """Test for case when deleting operation is successfull - entity is found and deleted."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_result = {"response": f"Entity '{entity['PartitionKey']}/{entity['RowKey']}' removed from table."}

        self.mock_table_client.delete_entity.return_value = None
        self.mock_table_client.get_entity.side_effect = azure_exceptions.ResourceNotFoundError(message="Not found.")

        test_result = entity_operations.delete(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=test_result, second=expected_result)

    def test_unsuccessfull_delete(self) -> None:
        """Test for case when deleting operation is unsuccessfull, meaning
        table_client.get_entity doesn't return ResourceNotFoundError."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"
        expected_error_message = f"Entity '{entity['PartitionKey']}/{entity['RowKey']}' NOT removed from table."

        self.mock_table_client.delete_entity.return_value = None
        self.mock_table_client.get_entity.side_effect = None

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.delete(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)

    def test_raises_error_if_resource_not_found_error(self) -> None:
        """Test for case when ResourceNotFoundError is raised by query_entities method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.delete_entity.side_effect = azure_exceptions.ResourceNotFoundError()

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.delete(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.mock_table_client.get_entity.assert_not_called()

    def test_raises_error_if_http_response_error(self) -> None:
        """Test for case when HttpResponseError is raised by query_entities method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.delete_entity.side_effect = azure_exceptions.ResourceNotFoundError(message="test error")
        self.mock_table_client.delete_entity.return_value = None

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.delete(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.mock_table_client.get_entity.assert_not_called()


class TestValidateResult(EntityOperationBaseTestCase):
    """Tests for entity_operations.validate_result function."""

    def test_successfull_validation(self) -> None:
        """Test for case when there is no discrepancy between the entity in the table and the entity to be inserted."""
        entity = {"PartitionKey": "test", "RowKey": "test"}

        self.mock_table_client.get_entity.return_value = entity

        # No exception should be raised
        entity_operations.validate_result(table_client=self.mock_table_client, entity=entity)

    def test_unsuccessfull_validation(self) -> None:
        """Test for case when there is a discrepancy between the entity in the table and the entity to be inserted."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        table_entity = {"PartitionKey": "test", "RowKey": "different"}
        expected_error_message = f"Entity in table: {table_entity}, entity to be inserted: {entity}."
        expected_error_summary = "EntityOperationFailed"

        self.mock_table_client.get_entity.return_value = table_entity

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.validate_result(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.assertEqual(first=cm.exception.message, second=expected_error_message)


class TestUpdate(EntityOperationBaseTestCase):
    """Tests for entity_operations.update function."""

    def setUp(self) -> None:
        """Extension of setUp method from EntityOperationBaseTestCase.
        Patching validate_results() method called within update() method."""
        super().setUp()
        self.patcher = patch("modules.entity_operations.validate_result")
        self.mock_validate_result = self.patcher.start()

    def tearDown(self) -> None:  # pylint: disable=C0103:invalid-name
        """Stops patching validate_results() method initaited by setUp method."""
        self.patcher.stop()
        super().tearDown()

    def test_successful_update(self) -> None:
        """Test for case when update operation is successful."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_result = {"response": f"Entity '{entity['PartitionKey']}/{entity['RowKey']}' updated."}

        self.mock_table_client.update_entity.return_value = None
        self.mock_validate_result.return_value = None

        test_result = entity_operations.update(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=test_result, second=expected_result)
        self.mock_validate_result.assert_called_once_with(table_client=self.mock_table_client, entity=entity)

    def test_unsuccessful_update_resource_not_found(self) -> None:
        """Test for case when ResourceNotFoundError is raised by update_entity method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.update_entity.side_effect = azure_exceptions.ResourceNotFoundError(message="Not found.")

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.update(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.mock_validate_result.assert_not_called()

    def test_unsuccessful_update_http_response_error(self) -> None:
        """Test for case when HttpResponseError is raised by update_entity method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.update_entity.side_effect = azure_exceptions.HttpResponseError(message="HTTP error")

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.update(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.mock_validate_result.assert_not_called()


class TestReset(EntityOperationBaseTestCase):
    """Tests for entity_operations.reset function."""

    def setUp(self) -> None:
        """Extension of setUp method from EntityOperationBaseTestCase.
        Patching validate_results() method called within update() method."""
        super().setUp()
        self.patcher = patch("modules.entity_operations.validate_result")
        self.mock_validate_result = self.patcher.start()

    def tearDown(self) -> None:  # pylint: disable=C0103:invalid-name
        """Stops patching validate_results() method initaited by setUp method."""
        self.patcher.stop()
        super().tearDown()

    def test_successful_reset(self) -> None:
        """Test for case when reset operation is successful."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_result = {"response": f"Entity '{entity['PartitionKey']}/{entity['RowKey']}' reset."}

        self.mock_table_client.update_entity.return_value = None
        self.mock_validate_result.return_value = None

        test_result = entity_operations.reset(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=test_result, second=expected_result)
        self.mock_validate_result.assert_called_once_with(table_client=self.mock_table_client, entity=entity)

    def test_unsuccessful_reset_resource_not_found(self) -> None:
        """Test for case when ResourceNotFoundError is raised by update_entity method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.update_entity.side_effect = azure_exceptions.ResourceNotFoundError()

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.reset(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.mock_validate_result.assert_not_called()

    def test_unsuccessful_reset_http_response_error(self) -> None:
        """Test for case when HttpResponseError is raised by update_entity method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.update_entity.side_effect = azure_exceptions.HttpResponseError()

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.reset(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.mock_validate_result.assert_not_called()


class TestInsert(EntityOperationBaseTestCase):
    """Tests for entity_operations.insert function."""

    def setUp(self) -> None:
        """Extension of setUp method from EntityOperationBaseTestCase.
        Patching validate_results() method called within update() method."""
        super().setUp()
        self.patcher = patch("modules.entity_operations.validate_result")
        self.mock_validate_result = self.patcher.start()

    def tearDown(self) -> None:  # pylint: disable=C0103:invalid-name
        """Stops patching validate_results() method initaited by setUp method."""
        self.patcher.stop()
        super().tearDown()

    def test_successful_insert(self) -> None:
        """Test for case when insert operation is successful."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_result = {"response": f"Entity '{entity['PartitionKey']}/{entity['RowKey']}' inserted."}

        self.mock_table_client.create_entity.return_value = None
        self.mock_validate_result.return_value = None

        test_result = entity_operations.insert(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=test_result, second=expected_result)
        self.mock_validate_result.assert_called_once_with(table_client=self.mock_table_client, entity=entity)

    def test_unsuccessful_insert_resource_exists(self) -> None:
        """Test for case when ResourceExistsError is raised by create_entity method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.create_entity.side_effect = azure_exceptions.ResourceExistsError()

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.insert(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.mock_validate_result.assert_not_called()

    def test_unsuccessful_insert_http_response_error(self) -> None:
        """Test for case when HttpResponseError is raised by create_entity method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.create_entity.side_effect = azure_exceptions.HttpResponseError()

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.insert(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.mock_validate_result.assert_not_called()


class TestUpsert(EntityOperationBaseTestCase):
    """Tests for entity_operations.upsert function."""

    def setUp(self) -> None:
        """Extension of setUp method from EntityOperationBaseTestCase.
        Patching validate_results() method called within update() method."""
        super().setUp()
        self.patcher = patch("modules.entity_operations.validate_result")
        self.mock_validate_result = self.patcher.start()

    def tearDown(self) -> None:  # pylint: disable=C0103:invalid-name
        """Stops patching validate_results() method initaited by setUp method."""
        self.patcher.stop()
        super().tearDown()

    def test_successful_upsert(self):
        """Test for case when upsert operation is successful."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_result = {"response": f"Entity '{entity['PartitionKey']}/{entity['RowKey']}' upserted."}

        self.mock_table_client.upsert_entity.return_value = None
        self.mock_validate_result.return_value = None

        test_result = entity_operations.upsert(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=test_result, second=expected_result)
        self.mock_validate_result.assert_called_once_with(table_client=self.mock_table_client, entity=entity)

    def test_unsuccessful_upsert_http_response_error(self):
        """Test for case when HttpResponseError is raised by upsert_entity method."""
        entity = {"PartitionKey": "test", "RowKey": "test"}
        expected_error_summary = "AzureError"

        self.mock_table_client.upsert_entity.side_effect = azure_exceptions.HttpResponseError()

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            entity_operations.upsert(table_client=self.mock_table_client, entity=entity)

        self.assertEqual(first=cm.exception.summary, second=expected_error_summary)
        self.mock_validate_result.assert_not_called()


if __name__ == "__main__":
    unittest.main()
