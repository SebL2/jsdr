"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
from http import HTTPStatus

from flask import Flask
from flask_restx import Resource, Api, reqparse
from flask_cors import CORS
import cities.cities as ct

app = Flask(__name__)
CORS(app)
api = Api(app)

READ = 'read'

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
MESSAGE = 'Message'

CITIES_EPS = '/cities'
CITIES_RESP = 'Cities'

SUCCESS = "Success"
ERROR = "Error"

NAME = 'name'
STATE_CODE = 'state_code'
POPULATION = 'population'

city_post = reqparse.RequestParser()
city_post.add_argument('name', type=str, required=True)
city_post.add_argument('state_code', type=str, required=True)
city_post.add_argument('population', type=int, required=True)

population_put = reqparse.RequestParser()
population_put.add_argument('city_id', type=str, required=True)
population_put.add_argument('population', type=int, required=True)

city_delete = reqparse.RequestParser()
city_delete.add_argument('city_id', type=str, required=True)


@api.route(f'{CITIES_EPS}')
class Cities(Resource):
    def get(self):
        try:
            cities = ct.read()
            return {CITIES_RESP: cities, "Number of cities": len(cities)}
        except ConnectionError:
            return {ERROR: "There is a connection error"}, \
                HTTPStatus.INTERNAL_SERVER_ERROR

    @api.expect(city_post)
    def post(self):
        args = city_post.parse_args()
        city = {
            NAME: args['name'],
            STATE_CODE: args['state_code'],
            POPULATION: args['population']
        }
        try:
            ct.create(city)
        except ValueError as e:
            return {ERROR: str(e)}, HTTPStatus.BAD_REQUEST
        return {SUCCESS: True}, HTTPStatus.CREATED

    @api.expect(population_put)
    def put(self):
        args = population_put.parse_args()
        city_id = args['city_id']
        population = args['population']

        # Validate population is not negative
        if population < 0:
            return {ERROR: "Population cannot be negative"}, \
                HTTPStatus.BAD_REQUEST

        try:
            ct.set_population(city_id, population)
        except ValueError as e:
            return {ERROR: str(e)}, HTTPStatus.BAD_REQUEST
        return {SUCCESS: True}

    @api.expect(city_delete)
    def delete(self):
        args = city_delete.parse_args()
        city_id = args['city_id']
        try:
            ct.delete(city_id)
        except ValueError as e:
            return {ERROR: str(e)}, HTTPStatus.BAD_REQUEST
        return {SUCCESS: True}


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    Provide a simple test endpoint to verify the application is working.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """
        endpoints = sorted(
            rule.rule for rule in api.app.url_map.iter_rules()
        )
        return {"Available endpoints": endpoints}


@api.route(f'{CITIES_EPS}/<string:city_id>')
class City(Resource):
    """
    Endpoint for operations on individual cities.
    """
    def get(self, city_id):
        """
        Get a specific city by ID.
        """
        try:
            cities = ct.read()
            if city_id not in cities:
                return {ERROR: f"City {city_id} not found"}, \
                    HTTPStatus.NOT_FOUND
            return {CITIES_RESP: cities[city_id]}
        except ConnectionError:
            return {ERROR: "There is a connection error"}, \
                HTTPStatus.INTERNAL_SERVER_ERROR
