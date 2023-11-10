# Azure Storage Table Connector

This application is an Azure Function that connects with Azure Storage Account `storksefdata5669832602` and performs various operations on the storage tables.

## Features

- Connects with Azure Storage Account
- Performs operations like get, update, insert, delete, upsert on the storage tables
- Can be triggered by an HTTP request

## How to Use

Send a POST request to the function's URL with the required body, depending on the table you connect with.

### Allowed Table Operations
See `modules.config.ALLOWED_OPERATIONS` for the supported table names.

### Allowed Table Names

See `modules.config.ALLOWED_TABLE_NAMES` for the supported table names.

### Request Body per table

#### Basic requirements
    
1. Requests body must be in JSON format.
2. Requests body must contain the following fields:

    ```json
    {
        "table_name": "<table_name>",
        "operation": "<operation>",
        "entity": {
            "RowKey": "<row_key>"
        }
    }
    ```
3.  Requirement for more `entity` fields depends on the table and operation.
4. Values of `table_name` and `operation` must be from the list of allowed values and in string format.
5. Values of `RowKey` and `PartitionKey` must be in string format.
6. All `date` values must be in string format and in the format `YYYY-MM-DD`.
7. All `datetime` values must be in string format and in the format `YYYY-MM-DDTHH:MM:SSZ`.
8. No `null` / `None` values allowed. Pass empty string instead. In case of empty `date_from`/`date_to` fields, pass `1970-01-01` and `2050-12-31` respectively.


#### Table: `ClientConfig`
Table storing list of clients and their configurations, excluding confidential information.
Used by TimerTrigger to get all the clients and their configurations.

For operations `get_all` (default behaviour of TimerTrigger):
```json
{
    "table_name": "ClientConfig",
    "operation": "get_all",
    "entity": {
        "RowKey": "_zakup" / "_sprzedaz"
    }
}
```

For all other operations:
```json
{
    "table_name": "ClientConfig",
    "operation": "get_all",
    "entity": {
        "PartitionKey": "<client's NIP>",
        "RowKey": "_zakup" / "_sprzedaz"
    }
}
```

#### Table: `SessionTokens`
Table for storing information on Session Token for KSeF session. Used by Orchestrator to get the Session Token. No confidential information stored.

For operations `get_all` (default behaviour of TimerTrigger):
```json
{
    "table_name": "ClientConfig",
    "operation": "get_all",
    "entity": {
        "RowKey": "_zakup" / "_sprzedaz"
    }
}
```

For all other operations:
```json
{
    "table_name": "ClientConfig",
    "operation": "get_all",
    "entity": {
        "PartitionKey": "<client's NIP>",
        "RowKey": "_zakup" / "_sprzedaz"
    }
}
```


#### Table: `ClientRules`
Table storing list of clients and their rules for processing invoices. Used by Downloader to assign custom GroupId to invoices.

#TODO - under development

## Installation
This project uses Python and pip for package management. Make sure you have them installed.

1. Clone the repository
2. Install the dependencies:

```bash
.venv\Scripts\python -m pip install -r requirements.txt 
```

3. Run the application:
```bash
.venv\Scripts\activate ; func host start 
```
