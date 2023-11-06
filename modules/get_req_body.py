"""modules for validating requests"""
import datetime
import logging

from azure import functions as func

from . import custom_error

log = logging.getLogger(name="log." + __name__)


def req_to_json(req: func.HttpRequest) -> dict:
    """Converts HTTP request to JSON. Raises TableOperationsError if request does not contain valid JSON data."""
    try:
        req_body = req.get_json()
        log.info(msg=f"StorageAccountConnector received request body: {req_body}")
        return req_body
    except ValueError as e:
        raise custom_error.TableOperationsError(
            summary="RequestError",
            message="HTTP request does not contain valid JSON data. Please check your request body.",
        ) from e


def parse_req_body(req_body: dict) -> tuple[dict, str, str]:
    """Parse HTTP request body."""
    try:
        entity = req_body["entity"]
        table_name = req_body["table_name"]
        operation = req_body["operation"]

    except KeyError as e:
        raise custom_error.TableOperationsError(
            summary="RequestError",
            message=f"KeyError while parsing request body: {e} not found.",
        ) from e
    except TypeError as e:
        raise custom_error.TableOperationsError(
            summary="RequestError",
            message=f"TypeError while parsing request body: {e}.",
        ) from e

    log.debug(
        msg=f"Request body parsed successfully. Entity: {entity}, table_name: {table_name}, operation: {operation}."
    )

    return entity, table_name, operation


def validate_requests_keys_are_allowed(key_name: str, key: str, allowed_values: list[str]) -> None:
    """Validates table name. Raises TableOperationsError if table name is not correct."""

    if key not in allowed_values:
        raise custom_error.TableOperationsError(
            summary="RequestError",
            message=f"{key_name} is not correct. Please choose one from '{allowed_values}'.",
        )


def validate_mandatory_entity_keys(mandatory_entity_keys: dict[str, list], entity: dict, table_name: str) -> None:
    """Validates if mandatory keys are present in entity. Raises TableOperationsError if any key is missing."""

    # lower case all keys before validation
    entity_keys = [key.lower() for key in entity.keys()]
    for key in mandatory_entity_keys[table_name]:
        if key not in entity_keys:
            raise custom_error.TableOperationsError(
                summary="RequestError",
                message=f"Entity does not contain mandatory key: {key}. Please check your request body.",
            )


def validate_partition_and_row_keys_are_strings(entity: dict) -> None:
    """Validates datatypes of entity's values. Raises TableOperationsError if any value is not a string."""

    for key in ["PartitionKey", "RowKey"]:
        try:
            if not isinstance(entity[key], str):
                raise custom_error.TableOperationsError(
                    summary="RequestError",
                    message=f"Value of {key} ({type(entity[key])}) is not a string. Please check your request body.",
                )
        except KeyError:
            # Check for mandatory keys was done one step earlier.
            # Therefore if "PartitionKey" or "RowKey" is missing, it is legal.
            continue


def convert_nulls_to_empty_string(entity: dict) -> dict:
    """Converts null values to empty strings in entity dict."""
    for key, value in entity.items():
        if value is None:
            entity[key] = ""
    return entity


def convert_datetime(date_string: str) -> datetime.datetime:
    """Convert datetime string to datetime ISO-formated object."""
    try:
        iso_formated_date = datetime.datetime.strptime(date_string, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError) as e:
        raise custom_error.TableOperationsError(
            summary="RequestError",
            message=f"Error while parsing {date_string} date. Please provide date in format 'YYYY-MM-DD'.",
        ) from e

    return iso_formated_date


def main(
    req: func.HttpRequest,
    allowed_table_names: list[str],
    allowed_operations: list[str],
    mandatory_entity_keys: dict[str, list],
) -> tuple[dict, str, str]:
    """
    Validates HTTP request body.

    Parameters:
        req (func.HttpRequest): HTTP request
        allowed_table_names (list[str]): List of allowed names of azure tables. Environment constant.
        allowed_operations (list[str]): List of allowed operations. Environment constant.
        mandatory_entity_keys (dict[str, list]): Dictionary with mandatory entity keys for each table.
            Environment constant.

    Returns:
        tuple[dict, str, str]: entity details, table_name, operation

    Raises:
        TableOperationsError: if any validation fails
    """
    req_body = req_to_json(req=req)

    entity, table_name, operation = parse_req_body(req_body=req_body)

    validate_requests_keys_are_allowed(key_name="Table name", key=table_name, allowed_values=allowed_table_names)

    validate_requests_keys_are_allowed(key_name="Operation", key=operation, allowed_values=allowed_operations)

    validate_mandatory_entity_keys(
        mandatory_entity_keys=mandatory_entity_keys,
        entity=entity,
        table_name=table_name,
    )

    validate_partition_and_row_keys_are_strings(entity=entity)

    entity = convert_nulls_to_empty_string(entity=entity)

    if "date_from" in entity:
        entity["date_from"] = convert_datetime(date_string=entity["date_from"])
    if "date_to" in entity:
        entity["date_to"] = convert_datetime(date_string=entity["date_to"])

    return entity, table_name, operation
