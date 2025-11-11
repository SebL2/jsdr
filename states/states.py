"""
City-level data for SWE project
"""

from data import db_connect as dbc

STATE_COLLECTION = "States"
ID = 'id'
COUNTRY_NAME = 'country_name'
STATE_CODE = 'state_code'
POPULATION = 'population'

SAMPLE_STATE = {
    COUNTRY_NAME: 'USA',
    STATE_CODE: 'NY',
    POPULATION: -1
}


def create(flds: dict) -> str:
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = dbc.create(STATE_COLLECTION, flds)
    return new_id


def num_cities() -> int:
    city_list = dbc.read(CITY_COLLECTION)
    return len(city_list)


def valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        raise ValueError(f'Bad type for {type(_id)=}')
    return len(_id) >= 1


def delete(name: str, state_code: str) -> bool:
    ret = dbc.delete(CITY_COLLECTION, {NAME: name, STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'City not found: {name}, {state_code}')
    return ret


def read() -> list:
    return dbc.read(CITY_COLLECTION)

def get_population(city_name: str, state_code: str) -> int:
  
    city = dbc.read_one(CITY_COLLECTION, {NAME: city_name, STATE_CODE: state_code})
    if not city:
        raise ValueError(f'City not found: {city_name}, {state_code}')
    return city.get(POPULATION, -1)


def set_population(city_name: str, state_code: str, population: int) -> bool:

    if not isinstance(population, int):
        raise ValueError(f'Bad type for {type(population)=}')
    if population < 0:
        raise ValueError('Population cannot be negative')

    city = dbc.read_one(CITY_COLLECTION, {NAME: city_name, STATE_CODE: state_code})
    if not city:
        raise ValueError(f'City does not exist: {city_name}, {state_code}')

    result = dbc.update(CITY_COLLECTION, {NAME: city_name, STATE_CODE: state_code}, {POPULATION: population})
    return result.modified_count > 0

def city_exists(city_id: str) -> bool:
    """Return True if a city with the given ID exists in the database. Dont return true if the city doesn't exist in the database"""
    cities = dbc.read(CITY_COLLECTION)
    return any(city.get(ID) == city_id for city in cities)
