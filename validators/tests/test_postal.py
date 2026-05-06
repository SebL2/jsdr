import pytest

from validators.postal import USPostalCode, UKPostalCode


def test_us_valid():
    p = USPostalCode('12345')
    assert str(p) == '12345'


def test_us_bad_type():
    with pytest.raises(TypeError):
        USPostalCode(12345)


def test_us_bad_length():
    with pytest.raises(ValueError):
        USPostalCode('1234')


def test_us_bad_chars():
    with pytest.raises(ValueError):
        USPostalCode('12A45')


def test_uk_valid_examples():
    # professor examples
    p = UKPostalCode('LO45 56HA')
    assert str(p) == 'LO45 56HA'
    p2 = UKPostalCode('L42 6HA')
    assert str(p2) == 'L42 6HA'


def test_uk_lowercase_accepted():
    p = UKPostalCode('lo45 56ha')
    assert str(p) == 'LO45 56HA'


def test_uk_bad_length():
    with pytest.raises(ValueError):
        UKPostalCode('A1 1')
