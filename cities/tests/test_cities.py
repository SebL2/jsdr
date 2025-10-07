import pytest

import cities.cities as ct

def test_create():
    with pytest.raises(ValueError):
        ct.create(17)

def test_success_create():
    old_length = ct.num_cities()
    new_id = ct.create(ct.SAMPLE.CITY)
    assert ct.valid_id(new_id)
    assert ct.num_cities > old_length