"""
Tests for database connection module.

Includes both a real integration test and mocked examples.
"""

from unittest.mock import patch

from server.db_connect import DBConnect
from data import db_connect as core_db


def test_db_connect_real_success():
    """
    Test DBConnect.connect() using the real underlying MongoDB connection.

    This verifies that our configuration (local or cloud MongoDB)
    is working end-to-end by performing a health check ping.
    """
    # Act: call the real connect method
    db_instance = DBConnect()
    client = db_instance.connect()

    # Assert: client object exists and health check passes
    assert client is not None
    assert core_db.health_check() is True

def test_list_collections_and_sample_documents():
    """
    Integration test that inspects available collections and prints
    one sample document (if any) from each.

    Run with `pytest -s` to see printed output.
    """
    client = core_db.connect_db()
    db_name = core_db.SE_DB
    db = client[db_name]

    # List collections
    collections = sorted(db.list_collection_names())
    print(f"Collections in '{db_name}': {collections}")

    # Grab at most one sample document per collection
    sample_docs = {}
    for coll in collections:
        doc = db[coll].find_one()
        if doc:
            sample_docs[coll] = doc

    print("Sample documents (one per non-empty collection):")
    for coll, doc in sample_docs.items():
        print(f"  {coll}: {doc}")

    # Basic assertion so the test has a check
    assert isinstance(collections, list)

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
