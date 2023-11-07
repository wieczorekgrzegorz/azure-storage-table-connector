"""HTTP trigger for Azure Function App. Connects with chosen Azure Storage Account."""
import logging

import azure.functions as func

from modules import config, main


log: logging.Logger = logging.getLogger(name="log." + __name__)
config.logger(level=logging.DEBUG)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

###########################
#  StorageTableConnector  #
#      (HTTPTrigger)      #
###########################


@app.function_name(name="azure_storage_table_connector")
@app.route(route="azure_storage_table_connector", methods=["POST"])
def storage_account_connector_api(
    req: func.HttpRequest,
) -> func.HttpResponse:
    """Azure Function triggered by HTTP request. Connects with Azure Storage Account and returns response in a format:
    {'query_result': str | dict | list, 'error': dict | None}

    Parameters:
        req (func.HttpRequest): HTTP request

    Returns:
        func.HttpResponse: HTTP response


    How to use:
    Send a request.post to the function's URL.

    Body required for operations "get" | "update" | "insert" | "delete" | "upsert":
        {
            "table_name" (str): "ClientRules",
            "operation" (str): "get" | "update" | "insert" | "delete" | "upsert",
            "entity" (dict[str,str]): {
                "PartitionKey": "nip",
                "RowKey": "id",
                "Replacing": "old_id"
                "Rule": "rule1",
                }
        }

    Body required for operation "get_all" (to be used by TimerTrigger):
        {
            "table_name" (str): "ClientTable",
            "operation" (str): "get_all" ,
            "entity" (dict[str,str]): {
                "RowKey": "_zakup" | "_sprzedaz",
                }
        }

    Entity for SessionTokens (dict[str,str|bool]):
    {
        "PartitionKey": "nip",
        "RowKey": "_zakup" | "_sprzedaz",
        "Locked": bool,
        "SessionActive": bool,
        "SessionExpiration": str(datetime.utcfromtimestamp(now() + timedelta(hours=2))),
    }

    Entity for ClientTable (dict[str,str|bool]):
    {
        'PartitionKey': 'nip',
        'RowKey': "_zakup" | "_sprzedaz",
        'Name': 'Mniej ulubiona firma',
        'Run_frequency_hours': 24}
        'Group_upload': bool,
        "PDF": bool,
        'last_successfull_download_run': str(datetime),
        'penultimate_successfull_download_run': str(datetime),
    """
    log.info(msg="StorageAccountConnector starting.")

    print("\n\nMethod: ", req.method)
    print("URL: ", req.url)
    print("Headers: ", dict(req.headers))
    print("Params: ", dict(req.params))
    print("Route Params: ", req.route_params, end="\n\n")

    return main.main(
        req=req,
        connection_string=config.STORAGE_TABLE_CONNECTION_STRING,
        allowed_table_names=config.ALLOWED_TABLE_NAMES,
        allowed_operations=config.ALLOWED_OPERATIONS,
    )
