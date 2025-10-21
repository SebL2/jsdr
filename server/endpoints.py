"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api  # , fields  # Namespace
from flask_cors import CORS

# import werkzeug.exceptions as wz
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
CITIES_CREATE = '/create'

SUCCESS = "Success"
ERROR = "Error"


@api.route(f'{CITIES_EPS}/{READ}')
class Cities(Resource):
    def get(self):
        try:
            cities = ct.read()
            return {CITIES_RESP: cities, "Number of cities": len(cities)}
        except ConnectionError:
            return {ERROR: "There is a connection error"}, 500

    def post(self):
        fields = request.get_json()
        try:
            ct.create(fields)
        except ValueError:
            return {ERROR: "There is a value error"}, 400
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
