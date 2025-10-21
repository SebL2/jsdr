"""
City-level data for SWE project
"""

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
    new_id = str(len(cities) + 1)
    cities[new_id] = flds
    return new_id


def num_cities() -> int:
    return len(cities)


def valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        raise ValueError(f'Bad type for {type(_id)=}')
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def delete(city_id: str) -> bool:
    if city_id not in cities:
        raise ValueError(f'City does not exist: {city_id}')
    del cities[city_id]
    return True


def read() -> dict:
    if not db_connect(1):
        raise ConnectionError('Could not connect to DB.')
    return cities

def get_population(city_id: str) -> int:
    if city_id not in cities:
        raise ValueError(f'City does not exist: {city_id}')
    return cities[city_id]['population']


def set_population(city_id: str,population: int) -> bool:
    if city_id not in cities:
        raise ValueError(f'City does not exist: {city_id}')
    if not isinstance(population,int):
         raise ValueError(f'Bad type for {type(population)=}')
    if population < 0:
        raise ValueError('Population cannot be negative')
    cities[city_id]['population'] = population
    return True