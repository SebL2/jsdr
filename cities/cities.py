"""
Cities Business Logic Module

Provides core business logic for managing city data with CRUD operations,
validation, and error handling.
"""

# Import database connection module
from data import db_connect as dbc

# Database collection name
CITY_COLLECTION = "Cities"

# Field name constants
ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'
POPULATION = 'population'

# Sample city data for testing
SAMPLE_CITY = {
    NAME: 'New York',
    STATE_CODE: 'NY',
    POPULATION: -1
}


def create(flds: dict) -> str:
    """
    Create a new city with validation.

    Args:
        flds (dict): City data with required 'name' field

    Returns:
        str: Unique ID of the created city

    Raises:
        ValueError: If input is invalid or name is missing
    """
    # Validate input type
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    # Validate required name field
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    # Create city in database
    new_id = dbc.create(CITY_COLLECTION, flds)
    return new_id


def num_cities() -> int:
    """Get total count of cities in the database."""
    city_list = dbc.read(CITY_COLLECTION)
    return len(city_list)


def valid_id(_id: str) -> bool:
    """
    Validate city ID format.

    Args:
        _id (str): ID to validate

    Returns:
        bool: True if ID is valid (non-empty string)
    """
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
    city = dbc.read_one(
        CITY_COLLECTION,
        {NAME: city_name, STATE_CODE: state_code},
    )
    if not city:
        raise ValueError(f'City not found: {city_name}, {state_code}')
    return city.get(POPULATION, -1)


def set_population(city_name: str, state_code: str, population: int) -> bool:
    """
    Update city population with validation.

    Args:
        city_name (str): Name of city to update
        state_code (str): State code of city
        population (int): New population (must be >= 0)

    Returns:
        bool: True if update successful

    Raises:
        ValueError: If population invalid or city not found
    """
    # Validate population type and value
    if not isinstance(population, int):
        raise ValueError(f'Bad type for {type(population)=}')
    if population < 0:
        raise ValueError('Population cannot be negative')

    # Check if city exists
    city = dbc.read_one(
        CITY_COLLECTION,
        {NAME: city_name, STATE_CODE: state_code},
    )
    if not city:
        raise ValueError(f'City does not exist: {city_name}, {state_code}')

    # Update population
    result = dbc.update(
        CITY_COLLECTION,
        {NAME: city_name, STATE_CODE: state_code},
        {POPULATION: population},
    )
    return result.modified_count > 0


def city_exists(city_id: str) -> bool:
    """
    Return True if a city with the given ID exists in the database.
    Do not return True if the city does not exist in the database.
    """
    cities = dbc.read(CITY_COLLECTION)
    return any(city.get(ID) == city_id for city in cities)
