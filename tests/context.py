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
FUNCTION_APP_PATH = str(PurePath(__file__).parents[1])
sys.path.insert(0, FUNCTION_APP_PATH)

# mock global variables for tests
os.environ["STORAGE_TABLE_CONNECTION_STRING"] = "mock_connection_string"


class BaseTestCase(unittest.TestCase):
    """
    A base test case class that sets up common functionality for all unit tests.

    This class handles the setup and teardown of resources common to all tests.
    It also sets up common mock objects and patches for logging.

    Attributes:
        mock_log: A mock object for the get_req_body.log module.
        mock_error_log: A mock object for the custom_error.log module.

    Methods:
        setUpClass: Class method called before running tests in an individual class.
        tearDownClass: Class method called after running all tests in an individual class.
        setUp: Instance method called before running each test method.
        tearDown: Instance method called after running each test method.
    """

    @classmethod
    def setUpClass(cls) -> None:
        print(f"\nRUNNING TESTS FOR: {cls.__name__}.")

    @classmethod
    def tearDownClass(cls) -> None:
        print("\nTESTS FINISHED")

    def setUp(self) -> None:
        self.mock_log = patch("modules.get_req_body.log").start()
        self.mock_error_log = patch("modules.custom_error.log").start()

    def tearDown(self) -> None:
        patch.stopall()
