"""
Flask REST API for Cities Management System

This module defines all the HTTP endpoints for our Flask application.
It provides a RESTful API for managing city data with full CRUD operations.

Key Features:
- Create, Read, Update, Delete cities
- Population management
- Error handling with proper HTTP status codes
- Input validation and parsing
- CORS support for cross-origin requests
"""

# Import HTTP status codes for proper REST API responses
from http import HTTPStatus

# Flask framework imports
from flask import Flask
from flask_restx import Resource, Api, reqparse
from flask_cors import CORS

# Import our cities business logic module
import cities.cities as ct

# Initialize Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing for web browser compatibility
# Configure CORS to allow requests from frontend
# This resolves CSRF-like issues by properly handling cross-origin requests
CORS(app, 
     resources={r"/*": {
         "origins": "*",  # In production, specify actual frontend domain
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "supports_credentials": False  # Set to True if using cookies/auth
     }})
# Create Flask-RESTX API instance for automatic documentation and validation
api = Api(app)

# Constants for API operations
READ = 'read'

# Endpoint URL constants - centralized for easy maintenance
ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
MESSAGE = 'Message'

CITIES_EPS = '/cities'
CITIES_RESP = 'Cities'

# Standard response message constants
SUCCESS = "Success"
ERROR = "Error"

# City field name constants - matches the cities module schema
NAME = 'name'
STATE_CODE = 'state_code'
POPULATION = 'population'

# Request parsers for input validation and automatic documentation
# These define what parameters each endpoint expects and their types

# Parser for POST /cities - creating new cities
city_post = reqparse.RequestParser()
city_post.add_argument('name', type=str, required=True,
                       help='City name is required')
city_post.add_argument('state_code', type=str, required=True,
                       help='State code is required (e.g., NY, CA)')
city_post.add_argument('population', type=int, required=True,
                       help='Population must be a positive integer')

# Parser for PUT /cities - updating city population
population_put = reqparse.RequestParser()
population_put.add_argument('city', type=str, required=True,
                            help='City is required')
population_put.add_argument('state', type=str, required=True,
                            help='State is required')
population_put.add_argument('population', type=int, required=True,
                            help='New population value')


# Parser for DELETE /cities - deleting cities
city_delete = reqparse.RequestParser()
city_delete.add_argument('city', type=str, required=True,
                         help='City to delete is required')
city_delete.add_argument('state', type=str, required=True,
                         help='State name to delete is required')


@api.route(f'{CITIES_EPS}')
class Cities(Resource):
    """
    RESTful endpoint for cities collection operations.

    This class handles HTTP requests to /cities and provides:
    - GET: Retrieve all cities
    - POST: Create a new city
    - PUT: Update city population
    - DELETE: Remove a city

    All methods include proper error handling and return appropriate
    HTTP status codes.
    """

    def get(self):
        """
        GET /cities - Retrieve all cities in the system.

        Returns:
            200: JSON object with cities data and count
            500: Internal server error if database connection fails

        Example response:
            {
                "Cities": {
                    "1": {
                        "name": "NYC",
                        "state_code": "NY",
                        "population": 8000000
                    }
                },
                "Number of cities": 1
            }
        """
        try:
            # Fetch all cities from database
            cities = ct.read()
            # Return cities with count for client convenience
            return {CITIES_RESP: cities, "Number of cities": len(cities)}
        except ConnectionError:
            # Handle database connection failures gracefully
            return {ERROR: "There is a connection error"}, \
                HTTPStatus.INTERNAL_SERVER_ERROR

    @api.expect(city_post)
    def post(self):
        """
        POST /cities - Create a new city.

        Expected JSON body:
            {
                "name": "City Name",
                "state_code": "ST",
                "population": 123456
            }

        Returns:
            201: City created successfully
            400: Bad request (invalid data, missing fields, etc.)

        The request parser automatically validates required fields and types.
        """
        # Parse and validate request arguments
        args = city_post.parse_args()
        # Build city object from request data
        city = {
            NAME: args['name'],
            STATE_CODE: args['state_code'],
            POPULATION: args['population']
        }
        # Additional validation: population must be non-negative
        if city[POPULATION] < 0:
            return {ERROR: "Population cannot be negative"}, \
                HTTPStatus.BAD_REQUEST
        try:
            # Delegate to business logic layer for creation
            ct.create(city)
        except ValueError as e:
            # Return validation errors to client
            return {ERROR: str(e)}, HTTPStatus.BAD_REQUEST
        # Return success with 201 Created status
        return {SUCCESS: True}, HTTPStatus.CREATED

    @api.expect(population_put)
    def put(self):
        """
        PUT /cities - Update a city's population.

        Expected parameters:
            city (str): ID of the city to update
            state (str): State of the city to delete
            population (int): New population value (must be >= 0)

        Returns:
            200: Population updated successfully
            400: Bad request (city not found, negative population, etc.)

        This endpoint includes validation to prevent negative
        population values.
        highkey sus
        """
        # Parse request parameters
        args = population_put.parse_args()
        city = args['city']
        state = args['state']
        population = args['population']

        # Validate population is not negative - business rule
        if population < 0:
            return {ERROR: "Population cannot be negative"}, \
                HTTPStatus.BAD_REQUEST

        try:
            # Update population through business logic layer
            ct.set_population(city, state, population)
        except ValueError as e:
            # Handle city not found or other validation errors
            return {ERROR: str(e)}, HTTPStatus.BAD_REQUEST
        return {SUCCESS: True}

    @api.expect(city_delete)
    def delete(self):
        """
        DELETE /cities - Remove a city from the system.

        Expected parameters:
            city (str): ID of the city to delete
            state (str): State of the city to delete

        Returns:
            200: City deleted successfully
            400: Bad request (city not found, invalid ID, etc.)

        This is a destructive operation that permanently removes the
        city.
        """
        # Parse delete request parameters
        args = city_delete.parse_args()
        city = args['city']
        state = args['state']
        try:
            # Perform deletion through business logic layer
            ct.delete(city, state)
        except ValueError as e:
            # Handle city not found errors
            return {ERROR: str(e)}, HTTPStatus.BAD_REQUEST
        return {SUCCESS: True}


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    Health check endpoint for monitoring and testing.

    This simple endpoint serves multiple purposes:
    - Verify the Flask application is running
    - Test basic HTTP connectivity
    - Provide a lightweight endpoint for load balancers
    - Serve as a starting point for API exploration
    """

    def get(self):
        """
        GET /hello - Simple health check endpoint.

        Returns:
            200: JSON response indicating the server is operational

        Example response:
            {"hello": "world"}

        This endpoint requires no authentication and has no side effects,
        making it perfect for automated health checks and monitoring
        systems.
        """
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    Self-documenting API endpoint discovery.

    This endpoint provides runtime discovery of all available API endpoints.
    It's particularly useful for:
    - API documentation and exploration
    - Client applications that need to discover available endpoints
    - Development and debugging
    - Integration testing
    """

    def get(self):
        """
        GET /endpoints - Discover all available API endpoints.

        Returns:
            200: JSON object with a sorted list of all endpoint URLs

        Example response:
            {
                "Available endpoints": [
                    "/cities",
                    "/cities/<string:city_id>",
                    "/endpoints",
                    "/hello"
                ]
            }

        This endpoint dynamically generates the list by inspecting
        Flask's URL routing table, so it's always up-to-date with the
        current API.
        """
        # Extract all URL rules from Flask's routing table
        endpoints = sorted(
            rule.rule for rule in api.app.url_map.iter_rules()
        )
        # Return sorted list for easy reading
        return {"Available endpoints": endpoints}


@api.route(f'{CITIES_EPS}/<string:city_id>')
class City(Resource):
    """
    RESTful endpoint for individual city operations.

    This endpoint handles operations on specific cities identified by their ID.
    The URL pattern /cities/<city_id> follows REST conventions where:
    - The resource collection is /cities
    - Individual resources are /cities/{id}

    This provides a clean, predictable API structure that clients can
    easily understand.
    """

    def get(self, city_id):
        """
        GET /cities/<city_id> - Retrieve a specific city by its ID.

        Args:
            city_id (str): The unique identifier of the city to retrieve

        Returns:
            200: JSON object containing the city data
            404: City not found
            500: Internal server error (database connection issues)

        Example response for GET /cities/1:
            {
                "Cities": {
                    "name": "New York",
                    "state_code": "NY",
                    "population": 8000000
                }
            }

        This endpoint is useful when clients need details about a
        specific city rather than retrieving the entire cities
        collection.
        """
        try:
            # Fetch all cities from database
            cities = ct.read()
            # Check if requested city exists
            if city_id not in cities:
                return {ERROR: f"City {city_id} not found"}, \
                    HTTPStatus.NOT_FOUND
            # Return the specific city data
            return {CITIES_RESP: cities[city_id]}
        except ConnectionError:
            # Handle database connection failures
            return {ERROR: "There is a connection error"}, \
                HTTPStatus.INTERNAL_SERVER_ERROR
