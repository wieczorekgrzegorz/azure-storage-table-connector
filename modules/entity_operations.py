"""GET, DELETE, UPDATE, INSERT, UPSERT operations on entities in azure Table."""
import datetime
import logging

import azure.core.exceptions as azure_exceptions

from azure.data.tables import TableClient, UpdateMode

from .utilities import custom_error

log = logging.getLogger(name="log.storage_account_connector." + __name__)

# more: https://learn.microsoft.com/en-us/python/api/overview/azure/data-tables-readme?view=azure-python


def get(table_client: TableClient, entity: dict) -> dict:
    """Lists entities in an azure Table.

    Parameters:
        table_client (TableClient): TableClient object
        entity (dict): dictionary with entity's PartitionKey and RowKey

    Returns:
        list[dict] | None: list of entities if found, None otherwise

    Raises:
        custom_error.TableOperationsError: if error occurs while listing entities from azure Table\
            or if no entities are found
    """
    entities_list = []
    try:
        queried_entities = table_client.query_entities(
            query_filter=f"PartitionKey eq '{entity['PartitionKey']}' and RowKey eq '{entity['RowKey']}'"
        )
        for element in queried_entities:
            entities_list.append(element)
    except (
        azure_exceptions.ResourceNotFoundError,
        azure_exceptions.HttpResponseError,
    ) as e:
        raise custom_error.TableOperationsError(summary="AzureError", message=e.message) from e

    if len(entities_list) == 0:
        raise custom_error.TableOperationsError(
            summary="NoEntity",
            message=f"No entities found for {entity['PartitionKey']}/{entity['RowKey']}.",
        )

    if len(entities_list) > 1:
        # this shouldn't be possible, as PartitionKey and RowKey are unique keys
        raise custom_error.TableOperationsError(
            summary="MoreThanOneEntityFound",
            message=f"More than one entity found for PartitionKey '{entity['PartitionKey']}'/\
                and RowKey '{entity['RowKey']}",
        )

    return entities_list[0]


def get_all(table_client: TableClient, entity: dict) -> list[dict]:
    """Lists entities in an azure Table.

    Parameters:
        table_client (TableClient): TableClient object
        entity (dict): dictionary with entity's PartitionKey and/or RowKey

    Returns:
        list[dict] | None: list of entities if found, None otherwise

    Raises:
        custom_error.TableOperationsError: if error occurs while listing entities from azure Table\
            or if no entities are found
    """

    entities_list = []
    try:
        if ("RowKey" in entity.keys()) and ("PartitionKey" in entity.keys()):
            query_filter = f"PartitionKey eq '{entity['PartitionKey']}' and RowKey eq '{entity['RowKey']}'"
        elif "RowKey" in entity.keys():
            query_filter = f"RowKey eq '{entity['RowKey']}'"
        elif "PartitionKey" in entity.keys():
            query_filter = f"PartitionKey eq '{entity['PartitionKey']}'"
        else:
            raise custom_error.TableOperationsError(
                summary="RequestError",
                message=f"Both 'PartitionKey' and 'RowKey' are missing from entity: {entity}. Provide at least one.",
            )

        queried_entities = table_client.query_entities(query_filter=query_filter)
        for element in queried_entities:
            entities_list.append(element)
    except (
        azure_exceptions.ResourceNotFoundError,
        azure_exceptions.HttpResponseError,
    ) as e:
        raise custom_error.TableOperationsError(summary="AzureError", message=e.message) from e

    if len(entities_list) == 0:
        raise custom_error.TableOperationsError(summary="NoEntity", message=f"No entities found for {entity}.")

    return entities_list


def delete(table_client: TableClient, entity: dict) -> dict:
    """Deletes the specified entity in a table.
    No error will be raised if the entity or PartitionKey-RowKey pairing is not found.

    Parameters:
        table_client (TableClient): TableClient object
        entity (dict): dictionary with entity's PartitionKey and RowKey

    Returns:
        dict | None: deleted entity if found, None otherwise

    Raises:
        custom_error.TableOperationsError: if entity was not removed from azure Table, as checked by\
            querying for the entity after delete operation.
    """
    try:
        table_client.delete_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])

        try:
            table_client.get_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])
        except azure_exceptions.ResourceNotFoundError:
            return {"response": f"Entity {entity['PartitionKey']} {entity['RowKey']} removed from table."}
    except (
        azure_exceptions.ResourceNotFoundError,
        azure_exceptions.HttpResponseError,
    ) as e:
        raise custom_error.TableOperationsError(summary="AzureError", message=e.message) from e

    raise custom_error.TableOperationsError(
        summary="AzureError",
        message=f"Entity '{entity['PartitionKey']}/{entity['RowKey']}' NOT removed from table.",
    )


def validate_result(table_client: TableClient, entity: dict) -> None:
    """Validates the specified entity in a table.

    Parameters:
        table_client (TableClient): TableClient object
        entity (dict): dictionary with entity's PartitionKey and RowKey

    Returns:
        dict | None: deleted entity if found, None otherwise

    Raises:
        custom_error.TableOperationsError: if discrepancy between entity in table and entity to be changed is found
    """

    check = table_client.get_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])

    discrepancy_found = False
    for key in entity.keys():
        if check[key] != entity[key]:
            discrepancy_found = True

    if discrepancy_found:
        raise custom_error.TableOperationsError(
            summary="EntityOperationFailed",
            message=f"Entity in table: {check}, entity to be inserted: {entity}.",
        )


def update(table_client: TableClient, entity: dict, update_mode: UpdateMode = UpdateMode.MERGE) -> dict:
    """Updates the specified entity in a table.

    Parameters:
        table_client (azure.data.tables.TableClient):
            TableClient object
        entity (dict):
            dictionary with entity's PartitionKey and RowKey
        update_mode (optional, azure.data.tables.UpdateMode):
            The update mode to apply to the entity. Defaults to UpdateMode.MERGE.

    Returns:
        dict: summary of the operation in {"response": "message"} format

    Raises:
        custom_error.TableOperationsError: if error occurs while inserting entity into azure Table
    """
    try:
        table_client.update_entity(mode=update_mode, entity=entity)
    except (
        azure_exceptions.ResourceNotFoundError,
        azure_exceptions.HttpResponseError,
    ) as e:
        raise custom_error.TableOperationsError(summary="AzureError", message=e.message) from e

    validate_result(table_client=table_client, entity=entity)

    return {"response": f"Entity {entity['PartitionKey']} {entity['RowKey']} updated."}


def reset(table_client: TableClient, entity: dict) -> dict:
    """Resets the specified entity in a table to default values.
    Required entity keys: PartitionKey, RowKey.

    Parameters:
        table_client (azure.data.tables.TableClient):
            TableClient object
        entity (dict):
            dictionary with entity's PartitionKey and RowKey
        update_mode (optional, azure.data.tables.UpdateMode):
            The update mode to apply to the entity. Defaults to UpdateMode.MERGE.

    Returns:
        dict: summary of the operation in {"response": "message"} format

    Raises:
        custom_error.TableOperationsError: if error occurs while inserting entity into azure Table
    """
    entity["SessionActive"] = False
    entity["SessionToken"] = ""
    entity["SessionExpiration"] = datetime.datetime(
        year=1970,
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=datetime.timezone.utc,
    )
    entity["SessionReferenceNumber"] = ""
    try:
        table_client.upsert_entity(entity=entity)
    except (
        azure_exceptions.ResourceNotFoundError,
        azure_exceptions.HttpResponseError,
    ) as e:
        raise custom_error.TableOperationsError(summary="AzureError", message=e.message) from e

    validate_result(table_client=table_client, entity=entity)

    return {"response": f"Entity {entity['PartitionKey']} {entity['RowKey']} reset."}


def insert(table_client: TableClient, entity: dict) -> dict:
    """Creates a new entity in a table.

    Parameters:
        table_client (TableClient): TableClient object
        entity (dict): dictionary with entity's PartitionKey and RowKey

    Returns:
        dict: summary of the operation in {"response": "message"} format

    Raises:
        custom_error.TableOperationsError: if error occurs while inserting entity into azure Table
            or if entity already exists
    """
    try:
        table_client.create_entity(entity=entity)
    except (
        azure_exceptions.ResourceExistsError,
        azure_exceptions.HttpResponseError,
    ) as e:
        raise custom_error.TableOperationsError(summary="AzureError", message=e.message) from e

    validate_result(table_client=table_client, entity=entity)

    return {"response": f"Entity {entity['PartitionKey']} {entity['RowKey']} inserted."}


def upsert(table_client: TableClient, entity: dict) -> dict:
    """Inserts or updates an entity within a table by merging new property values into the existing entity.

    Parameters:
        table_client (TableClient): TableClient object
        entity (dict): dictionary with entity's PartitionKey and RowKey

    Returns:
        dict: summary of the operation in {"response": "message"} format

    Raises:
        custom_error.TableOperationsError: if error occurs while upserting entity into azure Table
    """
    try:
        table_client.upsert_entity(entity=entity)
    except azure_exceptions.HttpResponseError as e:
        raise custom_error.TableOperationsError(summary="AzureError", message=e.message) from e

    validate_result(table_client=table_client, entity=entity)

    return {"response": f"Entity {entity['PartitionKey']} {entity['RowKey']} upserted."}
