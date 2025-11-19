"""
Tests for database connection module.

Demonstrates mocking database connections to avoid real DB dependencies.
"""

from unittest.mock import patch
from server.db_connect import DBConnect


@patch("server.db_connect.DBConnect.connect", autospec=True)
def test_db_connect_mocked_success(mock_connect):
    """
    Test DBConnect.connect() with mocking.

    Demonstrates: method mocking, autospec, mock verification.
    """
    # Arrange: Set up mock to return True
    mock_connect.return_value = True
    db_instance = DBConnect()

    # Act: Call the mocked connect method
    result = db_instance.connect()

    # Assert: Verify behavior and mock was called correctly
    assert result is True
    mock_connect.assert_called_once_with(db_instance)


@patch("server.db_connect.DBConnect")
def test_read(mock_db_connect):
    """
    Test reading from mocked DBConnect instance.

    Demonstrates: class mocking, return_value chaining.
    """
    # Arrange: Set up mock instance with read method
    mock_instance = mock_db_connect.return_value
    mock_instance.read.return_value = ["sample_row"]

    # Act: Call the mocked read method
    result = mock_instance.read()

    # Assert: Verify data returned and method called
    assert "sample_row" in result
    mock_instance.read.assert_called_once()
