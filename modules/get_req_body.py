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


def validate_requests_keys_are_allowed(
    operation: str,
    table_name: str,
    allowed_operations: list[str],
    allowed_table_names: list[str],
) -> None:
    """Validates request body keys. Raises TableOperationsError if any key is not allowed."""

    if operation not in allowed_operations:
        raise custom_error.TableOperationsError(
            summary="RequestError",
            message=f"Operation is not correct. Please choose one from '{allowed_operations}'.",
        )

    if table_name not in allowed_table_names:
        raise custom_error.TableOperationsError(
            summary="RequestError",
            message=f"Table name is not correct. Please choose one from '{allowed_table_names}'.",
        )


def validate_partition_and_row_keys_are_strings(entity: dict) -> None:
    """Confirms that if either PartitionKey or RowKey is present in entity dict, they are of string type.
    Raises TableOperationsError if any value is not a string."""

    for key in entity.keys():
        if key in ["PartitionKey", "RowKey"] and not isinstance(entity[key], str):
            raise custom_error.TableOperationsError(
                summary="RequestError",
                message=f"Value of {key} ({type(entity[key])}) is not a string. Please check your request body.",
            )


def convert_nulls_to_empty_string(entity: dict) -> dict:
    """Converts null values to empty strings in entity dict."""
    for key, value in entity.items():
        if value is None:
            entity[key] = ""
    return entity


def convert_datetime(date_string: str) -> datetime.datetime:
    """Convert datetime string to datetime ISO-formated object. Used for requests to update ClientRules table."""
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
) -> tuple[dict, str, str]:
    """
    Validates HTTP request body.

    Parameters:
        req (func.HttpRequest): HTTP request
        allowed_table_names (list[str]): List of allowed names of azure tables. Environment constant.
        allowed_operations (list[str]): List of allowed operations. Environment constant.

    Returns:
        tuple[dict, str, str]: entity details, table_name, operation

    Raises:
        TableOperationsError: if any validation fails
    """
    req_body = req_to_json(req=req)

    entity, table_name, operation = parse_req_body(req_body=req_body)

    validate_requests_keys_are_allowed(
        operation=operation,
        table_name=table_name,
        allowed_operations=allowed_operations,
        allowed_table_names=allowed_table_names,
    )

    validate_partition_and_row_keys_are_strings(entity=entity)

    entity = convert_nulls_to_empty_string(entity=entity)

    if table_name == "ClientRules":
        entity["date_from"] = convert_datetime(date_string=entity["date_from"])
        entity["date_to"] = convert_datetime(date_string=entity["date_to"])

    return entity, table_name, operation
