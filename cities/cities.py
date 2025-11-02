"""
City-level data for SWE project
"""

import data.db_connect as dbc

CITY_COLLECTION = "Cities"
ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'
POPULATION = 'population'

cities = {}

MIN_ID_LEN = 1

SAMPLE_CITY = {
    NAME: 'New York',
    STATE_CODE: 'NY',
    POPULATION: -1
}


def db_connect(success_ratio: int) -> bool:
    """
    Return True if connection successful to database
    """
    return success_ratio == 1


def create(flds: dict) -> str:
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = dbc.create(CITY_COLLECTION, flds)
    return new_id


def num_cities() -> int:
    return len(cities)


def valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        raise ValueError(f'Bad type for {type(_id)=}')
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def delete(name: str, state_code: str) -> bool:
    ret = dbc.delete(CITY_COLLECTION, {NAME: name, STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'City not found: {name}, {state_code}')
    return ret


def read() -> dict:
    return dbc.read(CITY_COLLECTION)


def get_population(city_id: str) -> int:
    if city_id not in cities:
        raise ValueError(f'City does not exist: {city_id}')
    return cities[city_id]['population']


def set_population(city_id: str, population: int) -> bool:
    if city_id not in cities:
        raise ValueError(f'City does not exist: {city_id}')
    if not isinstance(population, int):
        raise ValueError(f'Bad type for {type(population)=}')
    if population < 0:
        raise ValueError('Population cannot be negative')
    cities[city_id]['population'] = population
    return True


def city_exists(city_id: str) -> bool:
    """Return True if a city with the given ID exists in the database."""
    return city_id in cities
