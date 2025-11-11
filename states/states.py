"""
State-level data for SWE project
"""

from data import db_connect as dbc

STATE_COLLECTION = "States"

# Field names
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
    """Create a new state record in the database."""
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(COUNTRY_NAME) or not flds.get(STATE_CODE):
        raise ValueError(f'Missing required fields: {flds}')
    new_id = dbc.create(STATE_COLLECTION, flds)
    return new_id


def num_states() -> int:
    """Return the number of states in the database."""
    state_list = dbc.read(STATE_COLLECTION)
    return len(state_list)


def valid_id(_id: str) -> bool:
    """Check if a given state ID is valid."""
    if not isinstance(_id, str):
        raise ValueError(f'Bad type for {type(_id)=}')
    return len(_id.strip()) > 0


def delete(state_code: str) -> bool:
    """Delete a state by its code."""
    ret = dbc.delete(STATE_COLLECTION, {STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'State not found: {state_code}')
    return ret


def read() -> list:
    """Return all states from the database."""
    return dbc.read(STATE_COLLECTION)


def get_population(state_code: str) -> int:
    """Get the population for a given state."""
    state = dbc.read_one(STATE_COLLECTION, {STATE_CODE: state_code})
    if not state:
        raise ValueError(f'State not found: {state_code}')
    return state.get(POPULATION, -1)


def set_population(state_code: str, population: int) -> bool:
    """Set the population for a given state."""
    if not isinstance(population, int):
        raise ValueError(f'Bad type for {type(population)=}')
    if population < 0:
        raise ValueError('Population cannot be negative')

    state = dbc.read_one(STATE_COLLECTION, {STATE_CODE: state_code})
    if not state:
        raise ValueError(f'State does not exist: {state_code}')

    result = dbc.update(STATE_COLLECTION, {STATE_CODE: state_code}, {POPULATION: population})
    return result.modified_count > 0


def state_exists(state_id: str) -> bool:
    """Return True if a state with the given ID exists in the database."""
    states = dbc.read(STATE_COLLECTION)
    return any(state.get(ID) == state_id for state in states)
