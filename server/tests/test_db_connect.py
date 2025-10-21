from unittest.mock import patch
from server.db_connect import DBConnect

@patch("server.db_connect.DBConnect.connect", autospec=True)
def test_db_connect_mocked_success(mock_connect):
    # Arrange
    mock_connect.return_value = True
    db_instance = DBConnect()

    # Act
    result = db_instance.connect()

    # Assert
    assert result is True
    mock_connect.assert_called_once_with(db_instance)
