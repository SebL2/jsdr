# Import pytest for testing framework and decorators
import pytest
# Import the Flask endpoints module we're testing
import server.endpoints as ep


@pytest.fixture(scope='function')
def temp_city():
    """
    Provide a synthetic city id for tests that do not require a real DB.

    For tests like negative population validation, a real database record is
    unnecessary and causes flaky behavior when MongoDB isn't running.
    """
    return "test-city-id"


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


def test_endpoints_lists_hello():
    """
    Ensure the endpoint discovery includes the /hello route.
    """
    resp = TEST_CLIENT.get(ep.ENDPOINT_EP)
    data = resp.get_json()
    assert ep.ENDPOINT_RESP in data
    assert ep.HELLO_EP in data[ep.ENDPOINT_RESP]
