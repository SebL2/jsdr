"""
States Business Logic Module

Provides core business logic for managing state data with CRUD operations,
validation, and error handling. Similar to cities module but for state-level
geographic data.

Features:
- State creation and validation
- Population management
- Database abstraction
- Error handling and logging
"""

# Import database connection module for data persistence
from data import db_connect as dbc

# Database collection name for states
STATE_COLLECTION = "States"

# Field name constants - ensures consistency across the application
ID = 'id'
COUNTRY_NAME = 'country_name'
STATE_CODE = 'state_code'
POPULATION = 'population'

# Sample state data for testing and demonstration
SAMPLE_STATE = {
    COUNTRY_NAME: 'USA',
    STATE_CODE: 'NY',
    POPULATION: -1  # -1 indicates unknown population
}


def create(flds: dict) -> str:
    """
    Create a new state record with validation.

    Args:
        flds (dict): State data with required fields:
                    - country_name: Country name (required)
                    - state_code: State abbreviation (required)
                    - population: Population count (optional)

    Returns:
        str: Unique identifier for the newly created state

    Raises:
        ValueError: If input is invalid or required fields are missing
    """
    # Validate input type
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    # Validate required fields
    if not flds.get(COUNTRY_NAME) or not flds.get(STATE_CODE):
        raise ValueError(f'Missing required fields: {flds}')
    # Create state in database
    new_id = dbc.create(STATE_COLLECTION, flds)
    return new_id


def num_states() -> int:
    """
    Get total count of states in the database.

    Returns:
        int: Number of states currently stored
    """
    state_list = dbc.read(STATE_COLLECTION)
    return len(state_list)


def valid_id(_id: str) -> bool:
    """
    Validate state ID format.

    Args:
        _id (str): ID to validate

    Returns:
        bool: True if ID is valid (non-empty string after stripping)

    Raises:
        ValueError: If ID is not a string
    """
    if not isinstance(_id, str):
        raise ValueError(f'Bad type for {type(_id)=}')
    return len(_id.strip()) > 0


def delete(state_code: str) -> bool:
    """
    Delete a state by its state code.

    Args:
        state_code (str): State code to delete (e.g., 'NY', 'CA')

    Returns:
        bool: Number of documents deleted (should be 1)

    Raises:
        ValueError: If state not found
    """
    ret = dbc.delete(STATE_COLLECTION, {STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'State not found: {state_code}')
    return ret


def read() -> list:
    """
    Retrieve all states from the database.

    Returns:
        list: List of state dictionaries with all their data
    """
    return dbc.read(STATE_COLLECTION)


def get_population(state_code: str) -> int:
    """
    Get population for a specific state.

    Args:
        state_code (str): State code to look up (e.g., 'NY', 'CA')

    Returns:
        int: Population of the state, or -1 if unknown

    Raises:
        ValueError: If state not found
    """
    state = dbc.read_one(STATE_COLLECTION, {STATE_CODE: state_code})
    if not state:
        raise ValueError(f'State not found: {state_code}')
    return state.get(POPULATION, -1)


def set_population(state_code: str, population: int) -> bool:
    """
    Update population for a specific state.

    Args:
        state_code (str): State code to update (e.g., 'NY', 'CA')
        population (int): New population value (must be >= 0)

    Returns:
        bool: True if update was successful

    Raises:
        ValueError: If population invalid or state not found
    """
    # Validate population type and value
    if not isinstance(population, int):
        raise ValueError(f'Bad type for {type(population)=}')
    if population < 0:
        raise ValueError('Population cannot be negative')

    # Check if state exists
    state = dbc.read_one(STATE_COLLECTION, {STATE_CODE: state_code})
    if not state:
        raise ValueError(f'State does not exist: {state_code}')

    # Update population
    result = dbc.update(
        STATE_COLLECTION,
        {STATE_CODE: state_code},
        {POPULATION: population}
    )
    return result.modified_count > 0


def state_exists(state_id: str) -> bool:
    """
    Check if a state with the given ID exists in the database.

    Args:
        state_id (str): State ID to check for existence

    Returns:
        bool: True if state exists, False otherwise

    Note:
        Uses generator expression for efficient searching.
    """
    states = dbc.read(STATE_COLLECTION)
    return any(state.get(ID) == state_id for state in states)
