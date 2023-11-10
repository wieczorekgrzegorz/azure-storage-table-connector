# type: ignore # Pylance returns fake-negative import error. Imports here are used as context for unit tests.
# flake8: noqa: F401, F402 # imports in this file are used in other files
"""Context file for unit tests. 
Mocks environment variables and inserts main app folder to PATH.
Turns off logging for tested modules.
"""
import os
from pathlib import PurePath
import sys
import unittest
from unittest.mock import patch


# adding main app folder to PATH
FUNCTION_APP_PATH = str(object=PurePath(__file__).parents[1])
sys.path.insert(0, FUNCTION_APP_PATH)

from modules.utilities import custom_error  # pylint: disable=C0413:import-error # path update needed first


# mock global variables for tests
os.environ["STORAGE_TABLE_CONNECTION_STRING"] = "mock_connection_string"

# declare global constants
EXPECTED_EXCEPTION = custom_error.TableOperationsError  # pylint: disable=C0103:invalid-name # it's intended here
ERROR_AZURE_ERROR = "AzureError"
ERROR_NO_ENTITY = "NoEntity"
ERROR_MORE_THAN_ONE_ENTITY = "MoreThanOneEntityFound"
ERROR_ENTITY_OPERATION_FAILED = "EntityOperationFailed"
ERROR_REQUEST_ERROR = "RequestError"


class BaseTestCase(unittest.TestCase):
    """Silences logging for tested modules, provides constant string values for tested exceptions."""

    @classmethod
    def setUpClass(cls) -> None:
        print(f"\nRUNNING TESTS FOR: {cls.__name__}.")
        patch("modules.get_req_body.log").start()
        patch("modules.main.log").start()
        patch("modules.entity_operations.log").start()
        patch("modules.utilities.custom_error.log").start()
        cls.expected_exception = custom_error.TableOperationsError
        cls.error_azure_error = ERROR_AZURE_ERROR
        cls.error_no_entity = ERROR_NO_ENTITY
        cls.error_more_than_one_entity = ERROR_MORE_THAN_ONE_ENTITY
        cls.error_entity_operation_failed = ERROR_ENTITY_OPERATION_FAILED
        cls.error_request_error = ERROR_REQUEST_ERROR

    @classmethod
    def tearDownClass(cls) -> None:
        print("\nTESTS FINISHED")
        patch.stopall()
