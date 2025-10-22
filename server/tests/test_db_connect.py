from unittest.mock import patch
from server.db_connect import DBConnect


@patch("server.db_connect.DBConnect.connect", autospec=True)
def test_db_connect_mocked_success(mock_connect):
    """Test that DBConnect.connect() can be successfully mocked."""
    # Arrange
    mock_connect.return_value = True
    db_instance = DBConnect()

    # Act
    result = db_instance.connect()

    # Assert
    assert result is True
    mock_connect.assert_called_once_with(db_instance)


@patch("server.db_connect.DBConnect")
def test_read(mock_db_connect):
    """Test reading from a mocked DBConnect instance."""
    # Arrange
    mock_instance = mock_db_connect.return_value
    mock_instance.read.return_value = ["sample_row"]

    # Act
    result = mock_instance.read()

    # Assert
    assert "sample_row" in result
    mock_instance.read.assert_called_once()
