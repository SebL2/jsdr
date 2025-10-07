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

def create(flds: dict):
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = len(cities) + 1
    cities[new_id] = flds
    return new_id

def num_cities() -> int:
    return len(cities)

def valid_id(_id: int):
    if not isinstance(id, int):
        raise ValueError(f'Bad type for {type(id)=}')
    if len(str(_id)) < MIN_ID_LEN:
        return False
    return True