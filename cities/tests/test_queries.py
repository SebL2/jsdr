# Import patch to mock functions or objects during tests
from unittest.mock import patch

# Import pytest to define and manage test cases
import pytest

# Import the module we are testing — contains the queries for city data
import cities.queries as qry


# This test is intentionally skipped because it's an example of a *bad test*.
# The decorator below tells pytest to skip this test entirely when running.
@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_cities():
    # This test directly compares a function's output (num_cities)
    # with an internal data structure (city_cache) — which makes it fragile.
    # It depends too much on implementation details rather than behavior.
    assert qry.num_cities() == len(qry.city_cache)


# The @patch decorator replaces 'db_connect' inside 'cities.queries' with a mock.
# This prevents the test from actually connecting to a database.
# It will instead return True whenever 'qry.db_connect()' is called.
@patch('cities.queries.db_connect', return_value=True)
def test_read(mock_db_connect):
    # Call the function we’re testing (qry.read).
    # Since db_connect is mocked, this runs in isolation.
    cities = qry.read()
    
    # Check that the returned object is a dictionary.
    # This ensures qry.read() returns data in the expected format.
    assert isinstance(cities, dict)