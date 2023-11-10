"""Unit tests for modules.main.py"""
import unittest
from unittest.mock import Mock, patch, MagicMock

import azure.functions as func

from modules import main
from . import context


class TestBuildHTTPResponse(context.BaseTestCase):
    """Tests for build_http_response function."""

    def test_build_http_response(self) -> None:
        """Test valid input for build_http_response function."""
        response_dict = {"key": "value"}
        expected_http_response = func.HttpResponse(body='{"key": "value"}')

        http_response = main.build_http_response(response_dict=response_dict)

        self.assertEqual(first=http_response.get_body(), second=expected_http_response.get_body())

    def test_build_http_response_error(self) -> None:
        """Test error for build_http_response function."""
        response_dict = {"key": set()}  # sets are not JSON-serializable

        with self.assertRaises(expected_exception=self.expected_exception) as cm:
            main.build_http_response(response_dict=response_dict)

        self.assertEqual(first=cm.exception.summary, second="TypeError")
        self.assertTrue(expr="is not JSON serializable" in cm.exception.message)


if __name__ == "__main__":
    unittest.main()
