# Import pytest for testing framework and decorators
import pytest
# Import the Flask endpoints module we're testing
import server.endpoints as ep
# Import cities module for test data and operations
import cities.cities as ct


@pytest.fixture(scope='function')
def temp_city():
    """
    Pytest fixture that creates a temporary city for testing.

    This fixture demonstrates:
    - Setup: Creates a city before the test runs
    - Yield: Provides the city ID to the test function
    - Teardown: Cleans up by deleting the city after the test
    - Error handling: Gracefully handles cases where city was already deleted
    """
    new_rec_id = ct.create(ct.SAMPLE_CITY)
    yield new_rec_id
    try:
        ct.delete(new_rec_id)
    except ValueError:
        print('The record was already deleted.')


# Create a test client for making HTTP requests to our Flask app
TEST_CLIENT = ep.app.test_client()


def test_hello():
    """
    Test the /hello endpoint to ensure basic API functionality.

    This test verifies:
    - The endpoint responds to GET requests
    - The response contains the expected JSON structure
    - The response includes the correct greeting message

    This is a basic smoke test to ensure the API is running.
    """
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


@pytest.mark.skip(reason="Demonstration of pytest skip feature")
def test_skip_demo():
    """
    Example of using @pytest.mark.skip decorator.

    This test demonstrates how to skip tests using the decorator approach.
    Useful for:
    - Tests that are temporarily broken
    - Features not yet implemented
    - Tests that only run in specific environments
    """
    assert True


def test_skip_demo_inline():
    """
    Example of using pytest.skip() function call.

    This demonstrates conditional skipping within the test function.
    Useful for:
    - Skipping based on runtime conditions
    - Platform-specific tests
    - Tests that require certain dependencies
    """
    pytest.skip("Demonstration of inline skip call")


def test_bad_population(temp_city):
    """
    Test that the API properly validates population values.

    This test demonstrates:
    - Using a fixture (temp_city) to provide test data
    - Testing error handling and validation
    - Verifying HTTP status codes for bad requests
    - PUT request testing with query parameters

    Expected behavior: API should return 400 Bad Request for negative
    population.
    """
    resp = TEST_CLIENT.put(
        ep.CITIES_EPS,
        query_string={"city_id": temp_city, "population": -1},
    )
    assert resp.status_code == 400
