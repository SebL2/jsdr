"""
City-level data for SWE project
"""

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'

cities = {}

MIN_ID_LEN = 1

SAMPLE_CITY = {
    NAME: 'New York',
    STATE_CODE: 'NY',
}

def db_connect(success_ratio: int) -> bool:
    """
    Return True if connection successful to database 
    """
    return success_ratio == 1 


def create(flds: dict) -> int:
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = len(cities) + 1
    cities[new_id] = flds
    return new_id


def num_cities() -> int:    
    return len(cities)


def valid_id(_id: int) -> bool:
    if not isinstance(_id, int):
        raise ValueError(f'Bad type for {type(id)=}')
    if len(str(_id)) < MIN_ID_LEN:
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
