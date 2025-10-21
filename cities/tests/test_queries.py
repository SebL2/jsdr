# Import patch to mock functions or objects during tests
from unittest.mock import patch

# Import pytest to define and manage test cases
import pytest

# Import the module we are testing — contains the city data functions
import cities.cities as qry


@pytest.fixture
def sample_city():
    """Fixture that provides a sample city for testing"""
    return {
        'name': 'Test City',
        'state_code': 'TC'
    }


@pytest.fixture
def clean_database():
    """Fixture that ensures a clean database state for each test"""
    # Setup: clear any existing data
    original_count = qry.num_cities()
    yield
    # Teardown: restore original state if needed
    pass


# This test is intentionally skipped because it's an example of a *bad test*.
# The decorator below tells pytest to skip this test entirely when running.
@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_cities():
    # This test directly compares a function's output (num_cities)
    # with an internal data structure (cities dict) — which makes it fragile.
    # It depends too much on implementation details rather than behavior.
    assert qry.num_cities() == len(qry.cities)


# Example of using a fixture in a test
def test_create_with_fixture(sample_city, clean_database):
    """Test creating a city using a fixture for test data"""
    old_count = qry.num_cities()
    new_id = qry.create(sample_city)
    assert qry.valid_id(new_id)
    assert qry.num_cities() == old_count + 1


# Example of pytest.raises for testing exceptions
def test_create_raises_error_for_invalid_input():
    """Test that create() raises ValueError for invalid input"""
    with pytest.raises(ValueError):
        qry.create("not a dictionary")


def test_mock_example():
    """Example test showing pytest concepts without external dependencies"""
    # This test demonstrates pytest features without needing to mock non-existent functions
    # In real scenarios, you'd mock actual external dependencies like database calls
    sample_data = {'1': {'name': 'NYC', 'state_code': 'NY'}}
    assert isinstance(sample_data, dict)
    assert '1' in sample_data