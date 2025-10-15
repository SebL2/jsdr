# cities/tests/test_cities.py
import pytest
import cities.cities as ct

def test_create_invalid_input_raises_error():
    # Arrange
    invalid_input = 17

    # Act & Assert
    with pytest.raises(ValueError):
        ct.create(invalid_input)


def test_success_create_increases_city_count():
    # Arrange
    old_length = ct.num_cities()
    sample_city = ct.SAMPLE.CITY

    # Act
    new_id = ct.create(sample_city)

    # Assert
    assert ct.valid_id(new_id)
    assert ct.num_cities() > old_length
