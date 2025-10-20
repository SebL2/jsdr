# cities/tests/test_cities.py
from unittest.mock import patch
import pytest
import cities.cities as ct


@pytest.fixture(scope='function')
def temp_city():
    new_rec_id = ct.create(ct.SAMPLE_CITY)
    yield new_rec_id
    try:
        ct.delete(new_rec_id)
    except ValueError:
        print('The record was already deleted.')


def test_create_invalid_input_raises_error():
    # Arrange
    invalid_input = 17

    # Act & Assert
    with pytest.raises(ValueError):
        ct.create(invalid_input)


def test_success_create_increases_city_count():
    # Arrange
    old_length = ct.num_cities()
    sample_city = ct.SAMPLE_CITY

    # Act
    new_id = ct.create(sample_city)

    # Assert
    assert ct.valid_id(new_id)
    assert ct.num_cities() > old_length

def test_num_cities():
    old_length = ct.num_cities()
    sample_city = ct.SAMPLE_CITY
    ct.create(sample_city)
    assert ct.num_cities == old_length + 1
    
def test_create_bad_name():
    with pytest.raises(ValueError):
        ct.create({})

@patch('cities.queries.db_connect', return_value=True, autospec=True)
def test_delete(mock_db_connect, temp_city):
    ct.delete(temp_city)
    assert temp_city not in ct.read()


@patch('cities.queries.db_connect', return_value=True, autospec=True)
def test_delete_not_there(mock_db_connect):
    with pytest.raises(ValueError):
        ct.delete('some value that is not there')


@patch('cities.queries.db_connect', return_value=True, autospec=True)
def test_read(mock_db_connect, temp_city):
    cities = ct.read()
    assert isinstance(cities, dict)
    assert temp_city in cities


@patch('cities.queries.db_connect', return_value=False, autospec=True)
def test_read_cant_connect(mock_db_connect):
    with pytest.raises(ConnectionError):
        ct.read()