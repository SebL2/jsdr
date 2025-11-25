"""
Advanced pytest features demonstration for cities module.

Showcases testing techniques: fixtures, mocking, exception testing,
skip decorators, and multiple assertion strategies.
"""

# Import patch for mocking functions during tests
from unittest.mock import patch

# Import pytest framework for testing utilities
import pytest

# Import the cities module we're testing
import cities.cities as qry

# TODO: Add an integration test that uses the real MongoDB via
# data.db_connect (with CLOUD_MONGO / MONGO_URI) instead of mocks,
# to verify cloud DB connectivity end-to-end.


@pytest.fixture
def sample_city():
    """
    Fixture providing standardized test city data.

    Returns clean test data for each test function.
    """
    return {
        'name': 'Test City',
        'state_code': 'TC'
    }


@pytest.fixture
def clean_database():
    """
    Fixture ensuring clean database state for each test.

    Demonstrates setup/teardown pattern with yield.
    """
    # Setup: prepare clean state
    yield  # Test runs here
    # Teardown: clean up after test
    pass


@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_cities():
    """
    Example of BAD test - depends on internal implementation.

    Problems: tight coupling, fragile, tests HOW not WHAT.
    Better: test behavior, not implementation details.
    """
    assert qry.num_cities() == len(qry.cities)


def test_create_with_fixture(sample_city, clean_database):
    """
    Test demonstrating fixtures, mocking, and mock verification.

    Shows: fixture usage, multiple mocking, side effects,
    mock assertions, and behavior testing.
    """
    # Mock num_cities() to return 0, then 1 (simulates count increase)
    with patch("cities.cities.num_cities", side_effect=[0, 1]):
        # Mock create() to return predictable ID
        with patch("cities.cities.create", return_value="1") as mock_create:
            old_count = qry.num_cities()
            new_id = qry.create(sample_city)
            # Verify create() called with correct parameters
            mock_create.assert_called_once_with(sample_city)
            assert qry.valid_id(new_id)
            assert qry.num_cities() == old_count + 1


def test_create_raises_error_for_invalid_input():
    """
    Test exception handling using pytest.raises.

    Demonstrates: exception testing, input validation,
    negative testing (what should NOT work).
    """
    with pytest.raises(ValueError):
        qry.create("not a dictionary")


def test_mock_example():
    """Example test showing pytest concepts without external dependencies"""
    sample_data = {'1': {'name': 'NYC', 'state_code': 'NY'}}
    assert isinstance(sample_data, dict)
    assert '1' in sample_data


@patch("cities.cities.num_cities", return_value=42)
def test_num_cities_with_patch(mock_num_cities):
    """
    Example of using patch to mock a function call.
    Pretends that num_cities() always returns 42,
    simulating a mock database response. or not
    """
    result = qry.num_cities()
    mock_num_cities.assert_called_once()
    assert result == 42


@pytest.mark.skip(
    reason="Demonstration of skip feature — test temporarily disabled"
)
def test_skip_example():
    """Example of a skipped test to demonstrate pytest skip functionality"""
    assert False, "This test should be skipped"
