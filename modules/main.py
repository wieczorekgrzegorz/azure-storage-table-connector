"""Module for connecting to Azure Storage Account."""
import datetime
import json
import logging
import sys

from azure import functions as func
from azure.data.tables import TableServiceClient, TableClient, _deserialize

from . import entity_operations, get_req_body
from .utilities import custom_error

log = logging.getLogger(name="log." + __name__)


def build_http_response(response_dict: dict) -> func.HttpResponse:
    """Creates HTTP response from response dictionary.
    Raises TableOperationsError if response dictionary is not JSON-serializable."""
    try:
        log.debug(msg=f"Building HTTP response with response_dict: {response_dict}.")
        http_response = func.HttpResponse(body=json.dumps(obj=response_dict))
        log.info(msg=f"StorageAccountConnector finished a run with response: {response_dict}")
        return http_response
    except TypeError as e:
        raise custom_error.TableOperationsError(
            summary="TypeError",
            message=f"Error while building HTTP response: {e}.",
        ) from e


def query_table(
    operation: str,
    table_client: TableClient,
    entity: dict,
) -> dict | list[dict]:
    """Connects to Azure Storage Account and queries the table with specified operation.
    Uses getattr(entity_operations, operation) to get the function object from entity_operations module.
    getattr(entity_operations, operation) is a function object -> example:
        req_body["operation"] == "get" will result in
        entity_operations.get(table_client=table_client, entity=entity)
    """

    log.debug(msg=f"Querying table with operation: {operation}.")
    query_result = getattr(entity_operations, operation)(table_client=table_client, entity=entity)
    # //BUG: [KK-186] query_result is a list of dicts, but it's not JSON-serializable
    log.debug(msg=f"Query returned {type(query_result)}: {query_result}.")

    return query_result


def convert_tables_entity_datetime_to_string(
    query_result: dict | list[dict],
) -> dict | list[dict]:
    """Converts TablesEntityDatetime to datetime. If query_result is a list, it converts all items in the list."""

    if isinstance(query_result, list):
        for item in query_result:
            item = convert_tables_entity_datetime_to_string(query_result=item)

    if isinstance(query_result, dict):
        for key, value in query_result.items():
            if isinstance(value, _deserialize.TablesEntityDatetime):
                query_result[key] = str(datetime.datetime.fromisoformat(str(value)))

    return query_result


def main(  # pylint: disable=too-many-arguments, R0914:too-many-locals
    req: func.HttpRequest,
    connection_string: str,
    allowed_table_names: list[str],
    allowed_operations: list[str],
    datetime_fields: list[str],
) -> func.HttpResponse:
    """
    #TODO Work in Progress.

    Parameters:
        req_body (dict): HTTP request body
        connection_string (str): connection string to azure storage account
    """
    return_body_dict: dict = {
        "query_result": None,
        "error": None,
    }
    try:
        entity, table_name, operation = get_req_body.main(
            req=req,
            allowed_table_names=allowed_table_names,
            allowed_operations=allowed_operations,
            datetime_fields=datetime_fields,
        )

        table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)

        table_client = table_service_client.get_table_client(table_name=table_name)

        query_result = query_table(
            operation=operation,
            table_client=table_client,
            entity=entity,
        )

        return_body_dict["query_result"] = convert_tables_entity_datetime_to_string(query_result=query_result)

        return build_http_response(response_dict=return_body_dict)

    except custom_error.TableOperationsError as e:
        return_body_dict["query_result"] = None
        return_body_dict["error"] = {
            "error": e.summary,
            "message": e.message,
        }
        log.error(msg=f"TableOperationsError. {e.summary}: {e.message}")
        return build_http_response(response_dict=return_body_dict)

    except Exception as exc:  # pylint: disable=broad-except # it's intended here
        return_body_dict["query_result"] = None
        exc_type, exc_value, exc_tb = sys.exc_info()
        exc_value = str(object=exc_value).replace("'", "")
        return_body_dict["error"] = {"error": exc.__class__.__name__, "message": exc_value}
        log.error(msg=f"Unexpected error. {exc_type}: {exc_value}; traceback: {exc_tb}")
        print(f"\n     return_body_dict: {return_body_dict} (type: {type(return_body_dict)})")
        return build_http_response(response_dict=return_body_dict)
