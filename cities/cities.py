from random import randint
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
     # Simulates a database connection attempt — succeeds randomly based on success_ratio
    return randint(1, success_ratio) % success_ratio

def create(flds: dict):
    # Validates the input and creates a new city entry in the cities dictionary
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = len(cities) + 1
    cities[new_id] = flds
    return new_id

def num_cities() -> int:
    # Returns the total number of cities currently stored
    return len(cities)


def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True

def read() -> dict:
    if not lb_connect(3):
        raise ConnectionError('Could not connec to DB.')
    return city_cache


def main():
    print(read())


if __name__ == '__main__':
    main()
