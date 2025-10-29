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


@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_cities():
    """Skipped test that depends too much on internal structure"""
    assert qry.num_cities() == len(qry.cities)


def test_create_with_fixture(sample_city, clean_database):
    """Test creating a city using a fixture for test data"""
    old_count = qry.num_cities()
    new_id = qry.create(sample_city)
    assert qry.valid_id(new_id)
    assert qry.num_cities() == old_count + 1


def test_create_raises_error_for_invalid_input():
    """Test that create() raises ValueError for invalid input"""
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
    simulating a mock database response.
    """
    result = qry.num_cities()
    mock_num_cities.assert_called_once()
    assert result == 42

@pytest.mark.skip(reason="Demonstration of skip feature — test temporarily disabled")
def test_skip_example():
    """Example of a skipped test to demonstrate pytest skip functionality"""
    assert False, "This test should be skipped"
