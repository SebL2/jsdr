import pytest
import cities.cities as ct

# Test that creating a city with an invalid argument (non-dictionary input) 
# correctly raises a ValueError exception.
def test_create():
    with pytest.raises(ValueError):
        ct.create(17)

# Test that successfully creating a valid city increases the number of stored cities
# and that the returned city ID is valid.
def test_success_create():
    # Record the current number of cities before creation
    old_length = ct.num_cities()

    # Create a new city using a valid sample city object
    new_id = ct.create(ct.SAMPLE.CITY)

    # Verify that the returned city ID is valid
    assert ct.valid_id(new_id)

    # Verify that the total number of cities increased after creation
    assert ct.num_cities > old_length
