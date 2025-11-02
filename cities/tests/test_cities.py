# cities/tests/test_cities.py
from unittest.mock import patch
import pytest
import cities.cities as ct

@pytest.fixture(scope='function')
def temp_city():
    ct.create(ct.SAMPLE_CITY)
    yield ct.SAMPLE_CITY
    try:
        ct.delete(ct.SAMPLE_CITY["name"],ct.SAMPLE_CITY["state_code"])
    except ValueError:
        print('The record was already deleted.')
@pytest.mark.skip("temporarily disabled")
def test_create_invalid_input_raises_error():
    # Arrange
    invalid_input = 17

    # Act & Assert
    with pytest.raises(ValueError):
        ct.create(invalid_input)

@pytest.mark.skip("temporarily disabled")
def test_success_create_increases_city_count():
    # Arrange
    old_length = ct.num_cities()
    sample_city = ct.SAMPLE_CITY

    # Act
    new_id = ct.create(sample_city)

    # Assert
    assert ct.valid_id(new_id)
    assert ct.num_cities() > old_length

@pytest.mark.skip("temporarily disabled")
def test_num_cities():
    old_length = ct.num_cities()
    sample_city = ct.SAMPLE_CITY
    ct.create(sample_city)
    assert ct.num_cities() == old_length + 1
    

def test_create_bad_name():
    with pytest.raises(ValueError):
        ct.create({})

@pytest.mark.skip("temporarily disabled")
def test_change_population(temp_city):
    old_population = ct.get_population(temp_city)
    new_population = old_population+1
    ct.set_population(temp_city,new_population)
    assert new_population == ct.get_population(temp_city)
        

@pytest.mark.skip("temporarily disabled")
def test_delete(temp_city):
    ct.delete(temp_city)
    assert temp_city not in ct.read()


@pytest.mark.skip("temporarily disabled")
def test_delete_not_there():
    with pytest.raises(ValueError):
        ct.delete('some value that is not there')


def test_read(temp_city):
    cities = ct.read()
    assert isinstance(cities, list)
    del temp_city["_id"]
    assert temp_city in cities


@pytest.mark.skip("temporarily disabled")
def test_read_cant_connect():
    with pytest.raises(ConnectionError):
        ct.read()
