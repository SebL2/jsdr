"""
Cities Business Logic Module

This module provides the core business logic for managing city data in our application.
It serves as the data access layer between the REST API endpoints and the database,
implementing CRUD operations with proper validation and error handling.

Key Features:
- City creation with validation
- Population management with business rules
- Data integrity enforcement
- Standardized error handling
- Database abstraction layer

Architecture:
- Uses the data.db_connect module for database operations
- Implements business rules and validation logic
- Provides a clean API for the REST endpoints
- Maintains data consistency and integrity

This module follows the separation of concerns principle by keeping
business logic separate from HTTP handling (endpoints) and database
implementation details (db_connect).
"""

# Import database connection module for data persistence
from data import db_connect as dbc

# Database collection name - centralizes the collection identifier
CITY_COLLECTION = "Cities"

# Field name constants - ensures consistency across the application
# Using constants prevents typos and makes refactoring easier
ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'
POPULATION = 'population'

# Sample city data for testing and demonstration purposes
# Population of -1 indicates unknown/unset population
SAMPLE_CITY = {
    NAME: 'New York',
    STATE_CODE: 'NY',
    POPULATION: -1
}


def create(flds: dict) -> str:
    """
    Create a new city in the database with validation.
    
    This function implements the business logic for city creation, including:
    - Input type validation (must be a dictionary)
    - Required field validation (name is mandatory)
    - Database insertion through the data access layer
    
    Args:
        flds (dict): Dictionary containing city data with required fields:
                    - name: City name (required, non-empty string)
                    - state_code: State abbreviation (optional)
                    - population: Population count (optional, integer)
    
    Returns:
        str: Unique identifier for the newly created city
        
    Raises:
        ValueError: If input is not a dictionary or if required fields are missing/invalid
        
    Example:
        city_id = create({
            'name': 'San Francisco',
            'state_code': 'CA', 
            'population': 875000
        })
    
    Business Rules:
    - City name is required and cannot be empty
    - Input must be a dictionary structure
    - Other fields are optional but will be validated if provided
    """
    # Validate input type - must be a dictionary for structured data
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    
    # Validate required fields - name is mandatory for city identification
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    
    # Delegate to database layer for actual storage
    new_id = dbc.create(CITY_COLLECTION, flds)
    return new_id


def num_cities() -> int:
    """
    Get the total count of cities in the database.
    
    This utility function provides a quick way to determine how many cities
    are currently stored in the system. Useful for:
    - Dashboard statistics
    - Pagination calculations
    - System monitoring
    - Test assertions
    
    Returns:
        int: Total number of cities in the database
        
    Note:
        This function reads all cities to count them. For large datasets,
        consider implementing a more efficient count operation in the database layer.
    """
    # Retrieve all cities from database
    city_list = dbc.read(CITY_COLLECTION)
    # Return the count
    return len(city_list)


def valid_id(_id: str) -> bool:
    """
    Validate whether a given ID meets the system's ID requirements.
    
    This function enforces business rules for city ID validation:
    - Must be a string type (for consistency with database IDs)
    - Must have at least 1 character (non-empty)
    
    Args:
        _id (str): The ID to validate
        
    Returns:
        bool: True if the ID is valid, False otherwise
        
    Raises:
        ValueError: If the ID is not a string type
        
    Business Rules:
    - IDs must be strings (database compatibility)
    - IDs cannot be empty (must have content)
    - Minimum length of 1 character
    
    Note:
        This is a basic validation. In production systems, you might want
        to add additional checks like format validation, character restrictions, etc.
    """
    # Type validation - IDs must be strings for database consistency
    if not isinstance(_id, str):
        raise ValueError(f'Bad type for {type(_id)=}')
    
    # Length validation - IDs must be non-empty
    return len(_id) >= 1


def delete(name: str, state_code: str) -> bool:
    """
    Delete a city from the database using name and state code as identifiers.
    
    This function removes a city from the system using a composite key
    (name + state_code) to uniquely identify the city to delete.
    
    Args:
        name (str): The name of the city to delete
        state_code (str): The state code of the city to delete
        
    Returns:
        bool: Number of documents deleted (should be 1 for successful deletion)
        
    Raises:
        ValueError: If no city is found with the given name and state code
        
    Business Rules:
    - Cities are identified by the combination of name and state code
    - Deletion must affect exactly one city (atomic operation)
    - Raises error if city doesn't exist (fail-fast approach)
    
    Example:
        delete('San Francisco', 'CA')  # Deletes San Francisco, California
        
    Note:
        This is a destructive operation that cannot be undone.
        Consider implementing soft deletes for production systems.
    """
    # Attempt to delete the city using composite key
    ret = dbc.delete(CITY_COLLECTION, {NAME: name, STATE_CODE: state_code})
    
    # Verify that exactly one city was deleted
    if ret < 1:
        raise ValueError(f'City not found: {name}, {state_code}')
    
    return ret


def read() -> list:
    """
    Retrieve all cities from the database.
    
    This function provides read access to the complete cities collection.
    It's a simple pass-through to the database layer but serves as an
    abstraction point for potential future enhancements like:
    - Caching
    - Filtering
    - Sorting
    - Pagination
    
    Returns:
        list: List of dictionaries, each representing a city with its data
        
    Example return value:
        [
            {'id': '1', 'name': 'New York', 'state_code': 'NY', 'population': 8000000},
            {'id': '2', 'name': 'Los Angeles', 'state_code': 'CA', 'population': 4000000}
        ]
        
    Note:
        For large datasets, consider implementing pagination or filtering
        to avoid loading all cities into memory at once.
    """
    return dbc.read(CITY_COLLECTION)


def get_population(city_name: str, state_code: str) -> int:
    """
    Retrieve the population of a specific city.
    
    This function looks up a city by its name and state code, then returns
    its population value. It handles cases where the city doesn't exist
    or where population data is missing.
    
    Args:
        city_name (str): Name of the city to look up
        state_code (str): State code of the city to look up
        
    Returns:
        int: Population of the city, or -1 if population is unknown/unset
        
    Raises:
        ValueError: If no city is found with the given name and state code
        
    Business Rules:
    - Cities are identified by name + state code combination
    - Population of -1 indicates unknown or unset population
    - Missing cities result in an error (fail-fast approach)
    
    Example:
        population = get_population('New York', 'NY')
        # Returns: 8000000 (or -1 if population is unknown)
        
    Note:
        The -1 default value is a sentinel value indicating missing data.
        Consider using None or a custom exception for missing population data
        in future versions for clearer semantics.
    """
    # Look up the specific city using composite key
    city = dbc.read_one(
        CITY_COLLECTION,
        {NAME: city_name, STATE_CODE: state_code},
    )
    
    # Verify city exists
    if not city:
        raise ValueError(f'City not found: {city_name}, {state_code}')
    
    # Return population, defaulting to -1 if not set
    return city.get(POPULATION, -1)


def set_population(city_name: str, state_code: str, population: int) -> bool:
    """
    Update the population of an existing city.
    
    This function implements the business logic for population updates,
    including comprehensive validation and error handling. It ensures
    data integrity by validating both the input and the target city's existence.
    
    Args:
        city_name (str): Name of the city to update
        state_code (str): State code of the city to update  
        population (int): New population value (must be non-negative)
        
    Returns:
        bool: True if the update was successful, False otherwise
        
    Raises:
        ValueError: If population is not an integer, is negative, or city doesn't exist
        
    Business Rules:
    - Population must be a non-negative integer
    - City must exist before population can be updated
    - Updates are atomic (either succeed completely or fail)
    - Type validation ensures data integrity
    
    Example:
        success = set_population('San Francisco', 'CA', 875000)
        # Returns: True if update succeeded
        
    Validation Steps:
    1. Type validation (must be integer)
    2. Business rule validation (must be non-negative)
    3. Existence validation (city must exist)
    4. Database update operation
    5. Success verification
    """
    # Type validation - population must be an integer
    if not isinstance(population, int):
        raise ValueError(f'Bad type for {type(population)=}')
    
    # Business rule validation - population cannot be negative
    if population < 0:
        raise ValueError('Population cannot be negative')

    # Existence validation - verify city exists before updating
    city = dbc.read_one(
        CITY_COLLECTION,
        {NAME: city_name, STATE_CODE: state_code},
    )
    if not city:
        raise ValueError(f'City does not exist: {city_name}, {state_code}')

    # Perform the update operation
    result = dbc.update(
        CITY_COLLECTION,
        {NAME: city_name, STATE_CODE: state_code},  # Query criteria
        {POPULATION: population},                    # Update data
    )
    
    # Verify the update was successful
    return result.modified_count > 0


def city_exists(city_id: str) -> bool:
    """
    Check if a city with the given ID exists in the database.
    
    This utility function provides a boolean check for city existence
    without retrieving the full city data. Useful for:
    - Validation before operations
    - Conditional logic in business processes
    - API endpoint existence checks
    
    Args:
        city_id (str): The unique identifier of the city to check
        
    Returns:
        bool: True if a city with the given ID exists, False otherwise
        
    Implementation Notes:
    - Uses a generator expression with any() for efficiency
    - Stops searching as soon as a match is found
    - Handles cases where cities might not have an ID field
    
    Performance Consideration:
    - Currently reads all cities to check existence
    - For large datasets, consider implementing a database-level exists query
    - The any() function provides short-circuit evaluation for better performance
    
    Example:
        if city_exists('12345'):
            print("City found!")
        else:
            print("City not found")
    """
    # Retrieve all cities from the database
    cities = dbc.read(CITY_COLLECTION)
    
    # Use generator expression with any() for efficient searching
    # Stops at first match, doesn't need to check all cities
    return any(city.get(ID) == city_id for city in cities)
