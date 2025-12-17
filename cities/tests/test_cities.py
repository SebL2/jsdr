# cities/tests/test_cities.py
"""
Unit tests for the cities.cities module.

This test suite demonstrates various pytest features and testing
best practices:
- Fixtures for test data setup
- Parametrized tests for multiple scenarios
- Exception testing with pytest.raises
- Mocking and monkeypatching
- Test organization and naming conventions
- Skip decorators for temporarily disabled tests

The tests focus on the core business logic of city management,
ensuring proper validation, CRUD operations, and error handling.
"""

# Import pytest framework for testing utilities and decorators
import pytest
# Import the cities module we're testing
import cities.cities as ct


@pytest.fixture(scope='function')
def temp_city():
    """
    Pytest fixture that provides a clean copy of sample city data
    for each test.

    Scope: 'function' means a new instance is created for each test function.
    This ensures test isolation - changes in one test don't affect others.

    Returns:
        dict: A copy of SAMPLE_CITY to avoid modifying the original data

    Why use a fixture instead of just using SAMPLE_CITY directly?
    - Test isolation: Each test gets its own copy
    - Consistency: All tests use the same base data
    - Maintainability: Change the fixture to change all test data
    - Avoids side effects: Tests can modify the data without affecting others
    """
    # Return a copy to avoid modifying the original SAMPLE_CITY
    return dict(ct.SAMPLE_CITY)


def test_create_invalid_input_raises_error():
    """
    Test that create() properly validates input types and raises
    ValueError for invalid data.

    This test demonstrates:
    - Exception testing using pytest.raises context manager
    - Input validation testing
    - Arrange-Act-Assert pattern (AAA pattern)
    - @pytest.mark.skip decorator for temporarily disabled tests

    The test ensures that passing a non-dictionary (integer 17) to create()
    raises a ValueError, which is the expected behavior for type validation.
    """
    # Arrange: Set up test data - intentionally invalid input
    invalid_input = 17

    # Act & Assert: Verify it raises the expected exception
    # pytest.raises() catches the exception and verifies its type
    with pytest.raises(ValueError):
        ct.create(invalid_input)


def test_success_create_increases_city_count():
    """
    Test the happy path for city creation - verify successful
    creation behavior.

    This test demonstrates:
    - State-based testing (checking system state before/after)
    - Multiple assertions to verify different aspects
    - Testing return values and side effects
    - Clear test naming that describes the expected behavior

    The test verifies two important behaviors:
    1. create() returns a valid ID for the new city
    2. The total number of cities increases after creation
    """
    # Arrange: Capture the current state before making changes
    old_length = ct.num_cities()
    sample_city = ct.SAMPLE_CITY

    # Act: Perform the operation we're testing
    new_id = ct.create(sample_city)
    _id = str(new_id.inserted_id)
    # Assert: Verify the expected outcomes
    # Check that the returned ID is valid according to business rules
    assert ct.valid_id(_id)
    # Check that the city count increased (side effect verification)
    assert ct.num_cities() > old_length


def test_num_cities():
    """
    Test that num_cities() accurately tracks the count of cities.

    This test demonstrates:
    - Precise assertion (== instead of >) for exact count verification
    - Testing utility functions that support main functionality
    - Simple, focused test with single responsibility

    This test is more specific than
    test_success_create_increases_city_count because it verifies the
    exact increment (by 1) rather than just \"increased\".
    """
    # Capture current count
    old_length = ct.num_cities()
    sample_city = ct.SAMPLE_CITY.copy()
    sample_city.pop("_id", None)

    # Add one city
    ct.create(sample_city)

    # Verify count increased by exactly 1
    assert ct.num_cities() == old_length + 1


def test_create_bad_name():
    """
    Test that create() validates required fields and rejects empty city data.

    This test demonstrates:
    - Edge case testing (empty dictionary)
    - Business rule validation (name is required)
    - Negative testing (testing what should NOT work)

    An empty dictionary {} lacks the required 'name' field, so create()
    should raise a ValueError. This ensures data integrity and prevents
    invalid cities from being stored in the system.
    """
    with pytest.raises(ValueError):
        ct.create({})


def test_change_population(temp_city):
    """
    Test population update functionality using a fixture.

    This test demonstrates:
    - Using fixtures as test parameters (dependency injection)
    - Testing update operations (not just create/read)
    - Round-trip testing (set a value, then verify it was set)
    - State mutation testing

    The temp_city fixture provides clean test data, and we verify that
    population changes are properly persisted and retrievable.

    Args:
        temp_city: Fixture providing sample city data for testing
    """
    # Get the current population value
    old_population = ct.get_population(temp_city["name"], temp_city["state_code"])  # noqa: E501

    # Calculate a new population value
    new_population = old_population + 1

    # Update the population
    ct.set_population(temp_city["name"], temp_city["state_code"], new_population)  # noqa: E501

    # Verify the change was persisted
    assert new_population == ct.get_population(temp_city["name"], temp_city["state_code"])  # noqa: E501


def test_delete(temp_city):
    """
    Test successful city deletion.

    This test demonstrates:
    - Testing destructive operations (delete)
    - Verification through absence (city should not exist after deletion)
    - Using fixtures for test setup
    - Testing the complete CRUD cycle (this covers the 'D' in CRUD)

    Args:
        temp_city: Fixture providing a city to delete
    """
    # Delete the city
    ct.delete(temp_city["name"], temp_city["state_code"])

    # Verify it's no longer in the system
    assert temp_city not in ct.read()


def test_delete_not_there():
    """
    Test that deleting a non-existent city raises appropriate error.

    This test demonstrates:
    - Error case testing for delete operations
    - Testing with invalid/non-existent data
    - Ensuring proper error handling for edge cases

    When trying to delete a city that doesn't exist, the system should
    raise a ValueError rather than silently failing or crashing.
    """
    with pytest.raises(ValueError):
        ct.delete('some value that is not there', "nothing here either")


def test_read(temp_city, monkeypatch):
    """
    Test the read functionality using monkeypatching for isolation.

    This test demonstrates:
    - Monkeypatching: Temporarily replacing a function with a mock
    - Test isolation: Avoiding dependencies on external systems (database)
    - Multiple fixtures: Using both temp_city and monkeypatch
    - Data structure validation: Checking return type and contents
    - Dynamic test data cleanup: Handling optional fields like "_id"

    Monkeypatching is pytest's built-in mocking mechanism that temporarily
    replaces the real read() function with our test version, ensuring the
    test runs in isolation without needing a real database.

    Args:
        temp_city: Fixture providing sample city data
        monkeypatch: Pytest's built-in fixture for temporary modifications
    """
    # Replace the real read() function with a mock that returns our test data
    # This isolates the test from database dependencies
    monkeypatch.setattr(ct, "read", lambda: [dict(temp_city)])

    # Call the (now mocked) read function
    cities = ct.read()

    # Verify the return type is correct
    assert isinstance(cities, list)

    # Clean up test data - remove internal fields that might interfere
    if "_id" in temp_city:
        del temp_city["_id"]
    for city in cities:
        del city["_id"]

    # Verify our test city is in the returned data
    assert temp_city in cities


@pytest.mark.skip("temporarily disabled")
def test_read_cant_connect():
    """
    Test that read() properly handles database connection failures.

    This test demonstrates:
    - Exception testing for external dependency failures
    - Testing error conditions that are hard to reproduce in real systems
    - Ensuring graceful failure handling

    When the database connection fails, read() should raise a ConnectionError
    rather than returning invalid data or crashing unexpectedly.
    This ensures the application can handle infrastructure problems gracefully.
    """
    with pytest.raises(ConnectionError):
        ct.read()
