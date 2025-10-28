from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest
import server.endpoints as ep
import cities.cities as ct

@pytest.fixture(scope='function')
def temp_city():
    new_rec_id = ct.create(ct.SAMPLE_CITY)
    yield new_rec_id
    try:
        ct.delete(new_rec_id)
    except ValueError:
        print('The record was already deleted.')


TEST_CLIENT = ep.app.test_client()


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json

    
@pytest.mark.skip(reason="Demonstration of pytest skip feature")
def test_skip_demo():
    assert True


def test_skip_demo_inline():
    pytest.skip("Demonstration of inline skip call")


def test_bad_population(temp_city):
    resp = TEST_CLIENT.put(ep.CITIES_EPS,query_string={"city_id": temp_city, "population": -1})
    assert resp.status_code == 400
        