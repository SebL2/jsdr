"""
Flask REST API for Cities Management System

This module defines all the HTTP endpoints for our Flask application.
It provides a RESTful API for managing city data with full CRUD operations.

Work in progress - Adding Multi-var parsing thorugh cities directory

Key Features:
- Create, Read, Update, Delete cities
- Population management
- Error handling with proper HTTP status codes
- Input validation and parsing
- CORS support for cross-origin requests
- manipulation cursed technique
"""

# Import HTTP status codes for proper REST API responses
from http import HTTPStatus
import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# Flask framework imports
from flask import Flask, redirect, request
from flask_restx import Resource, Api, reqparse
from flask_cors import CORS

# Import our cities business logic module
import cities.cities as ct

# Import cost-of-living module
import cost_of_living.cost_of_living as col

_FALLBACK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data', 'bkup', 'cities.json',
)
try:
    with open(_FALLBACK_PATH, 'r') as f:
        FALLBACK_CITIES = json.load(f)
except Exception:
    FALLBACK_CITIES = []

# Initialize Flask application
app = Flask(__name__)
# CORS for frontend: allow cross-origin
# requests (avoids browser blocking / CSRF-like issues)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {
        "origins": [
            "http://localhost:5173",
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
    }},
)
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

# Cost-of-living endpoint constants
COL_EP = '/cost-of-living'
SALARY_EP = '/cost-of-living/salary-adjustment'

# Recommendations / Smart City Finder
RECOMMENDATIONS_EP = '/recommendations'

# Google OAuth / Sign-In
GOOGLE_AUTH_EP = '/auth/google'
AUTH_ME_EP = "/auth/me"
AUTH_LOGOUT_EP = '/auth/logout'
GOOGLE_AUTH_CALLBACK_EP = '/auth/google/callback'

# OAuth persistence (MongoDB Geo DB via data.db_connect)
OAUTH_USERS_COLLECTION = 'Users'
OAUTH_SESSIONS_COLLECTION = 'Sessions'
USER_PROFILES_COLLECTION = 'UserProfiles'

# Profile endpoints
PROFILE_EP = '/auth/me/profile'
FAVORITES_EP = '/auth/me/favorites'
COMPARISONS_EP = '/auth/me/comparisons'
WEIGHTS_EP = '/auth/me/weights'

POST_LOGIN_REDIRECT = os.environ.get(
    'POST_LOGIN_REDIRECT',
    'http://localhost:5173',
)
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 7


def _google_oauth_credentials():
    return (
        os.environ.get('GOOGLE_CLIENT_ID'),
        os.environ.get('GOOGLE_CLIENT_SECRET'),
        os.environ.get('GOOGLE_REDIRECT_URI'),
    )


def _oauth_http_post_form(url: str, data: dict) -> dict:
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url,
        data=encoded,
        method='POST',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ''
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            raise ValueError(f'HTTP {e.code}: {body}') from e


def _oauth_http_get_json(url: str, headers=None) -> dict:
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _google_oauth_authorize_url() -> str:
    cid, secret, redir = _google_oauth_credentials()
    if not cid or not secret or not redir:
        raise ValueError(
            'Set environment variables for Google OAuth'
        )
    params = {
        'client_id': cid,
        'redirect_uri': redir,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    return (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        + urllib.parse.urlencode(params)
    )


def _google_exchange_code_for_tokens(code: str) -> dict:
    cid, secret, redir = _google_oauth_credentials()
    return _oauth_http_post_form(
        'https://oauth2.googleapis.com/token',
        {
            'client_id': cid,
            'client_secret': secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redir,
        },
    )


def _google_fetch_userinfo(access_token: str) -> dict:
    return _oauth_http_get_json(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        {'Authorization': f'Bearer {access_token}'},
    )


def _find_or_create_oauth_user(email: str, name: str, avatar_url: str) -> str:
    from data import db_connect as dbc

    doc = dbc.read_one(OAUTH_USERS_COLLECTION, {'email': email})
    if not doc:
        ins = dbc.create(
            OAUTH_USERS_COLLECTION,
            {'email': email, 'name': name, 'avatar_url': avatar_url},
        )
        return str(ins.inserted_id)
    dbc.update(
        OAUTH_USERS_COLLECTION,
        {'email': email},
        {'name': name, 'avatar_url': avatar_url},
    )
    return str(doc['_id'])


def _create_oauth_session(user_id: str) -> str:
    from data import db_connect as dbc

    token = secrets.token_hex(32)
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    dbc.create(
        OAUTH_SESSIONS_COLLECTION,
        {'token': token, 'user_id': user_id, 'expires': expires},
    )
    return token


def _session_cookie_secure() -> bool:
    """Default True so cross-site (SameSite=None) cookies are accepted."""
    raw = os.environ.get('SESSION_COOKIE_SECURE')
    if raw is None:
        return True
    return raw.lower() in ('1', 'true', 'yes')


def _session_cookie_samesite() -> str:
    """Cross-site fetches from frontend require SameSite=None."""
    return os.environ.get('SESSION_COOKIE_SAMESITE', 'None')


def _oauth_user_from_request():
    """
    Load the Users document for the current request's session cookie.

    Returns the user dict if the session cookie is present, valid, and not
    expired; otherwise None.
    """
    from bson import ObjectId
    from data import db_connect as dbc

    token = request.cookies.get('session')
    if not token:
        return None

    sess = dbc.read_one(OAUTH_SESSIONS_COLLECTION, {'token': token})
    if not sess:
        return None

    expires = sess.get('expires')
    if expires is None:
        return None
    now = datetime.now(timezone.utc)
    if getattr(expires, 'tzinfo', None) is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        return None

    user_id = sess.get('user_id')
    if not user_id:
        return None

    try:
        oid = ObjectId(user_id)
    except Exception:
        return None

    return dbc.read_one(OAUTH_USERS_COLLECTION, {'_id': oid})


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

# Parser for salary adjustment query parameters
salary_adj_parser = reqparse.RequestParser()
salary_adj_parser.add_argument('salary', type=float, required=True,
                               help='Annual salary is required')
salary_adj_parser.add_argument('from_city', type=str, required=True,
                               help='Origin city is required')
salary_adj_parser.add_argument('to_city', type=str, required=True,
                               help='Target city is required')


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
        """GET /cities"""
        cities = ct.read()
        if not cities:
            cities = FALLBACK_CITIES
            # stick it in cache so we don't retry DB every request
            from data import db_connect as dbc
            dbc._cache[(ct.CITY_COLLECTION, dbc.SE_DB, True)] = cities
        return {CITIES_RESP: cities, "Number of cities": len(cities)}

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


@api.route(f'{CITIES_EPS}/<string:city_id>/exists')
class CityExists(Resource):
    """
    Check if a city with the given ID exists.
    """

    def get(self, city_id):
        """
        GET /cities/<city_id>/exists - Check if a city exists.

        Returns:
            200: JSON with "exists" (bool)
        """
        try:
            found = ct.city_exists(city_id)
            return {"exists": found}
        except ConnectionError:
            return {ERROR: "There is a connection error"}, \
                HTTPStatus.INTERNAL_SERVER_ERROR


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


@api.route(COL_EP)
class CostOfLiving(Resource):
    """
    Cost-of-living index endpoint.

    Returns cost-of-living indices for all tracked cities.
    Index value of 100 = US national average.
    """

    def get(self):
        """
        GET /cost-of-living - Retrieve all city COL indices.

        Returns:
            200: JSON object with city names mapped to COL index values
        """
        data = col.get_all()
        return {"cost_of_living": data, "count": len(data)}


@api.route(SALARY_EP)
class SalaryAdjustment(Resource):
    """
    Salary adjustment calculator endpoint.

    Compares purchasing power between two cities by adjusting
    a salary based on cost-of-living differences.
    """

    @api.expect(salary_adj_parser)
    def get(self):
        """
        GET /cost-of-living/salary-adjustment - Calculate adjusted salary.

        Query params:
            salary (float): Current annual salary
            from_city (str): Origin city name
            to_city (str): Target city name

        Returns:
            200: JSON with original and adjusted salary details
            400: Bad request (negative salary)
            404: City not found in dataset
        """
        args = salary_adj_parser.parse_args()
        salary = args['salary']
        from_city = args['from_city']
        to_city = args['to_city']

        if salary < 0:
            return {ERROR: "Salary cannot be negative"}, \
                HTTPStatus.BAD_REQUEST

        try:
            result = col.adjust_salary(salary, from_city, to_city)
            return result
        except ValueError as e:
            return {ERROR: str(e)}, HTTPStatus.NOT_FOUND


# Parser for recommendations / smart city finder
recommendations_parser = reqparse.RequestParser()
recommendations_parser.add_argument(
    'salary', type=float, required=False,
    help='Current annual salary for equivalence calc',
)
recommendations_parser.add_argument(
    'state', type=str, required=False,
    help='Filter by state code (e.g. TX, CA)',
)
recommendations_parser.add_argument(
    'size', type=str, required=False,
    help='City size: small (<100k), medium (100k-500k), large (>500k), any',
)
recommendations_parser.add_argument(
    'top_n', type=int, required=False,
    help='Number of results to return (default 10, max 50)',
)


def _affordability_score(col_index: float) -> int:
    """Convert a COL index (NYC=100) to a 0-100 affordability score."""
    return max(0, min(100, round((105 - col_index) / 70 * 100)))


def _qol_score(affordability: int, population: int) -> int:
    """
    Derive a simple quality-of-life score.
    Weighs affordability (50%) and city-size proxy (30%) + baseline (20%).
    """
    if population >= 500_000:
        size_score = 90
    elif population >= 100_000:
        size_score = 70
    else:
        size_score = 45
    return max(0, min(100, round(0.5 * affordability + 0.3 * size_score + 20)))


@api.route(RECOMMENDATIONS_EP)
class Recommendations(Resource):
    """
    Smart City Finder — return cities ranked by affordability.

    Joins the cities collection with cost-of-living data and applies
    optional filters for state, city size, and salary equivalence.
    """

    @api.expect(recommendations_parser)
    def get(self):
        """
        GET /recommendations — ranked city recommendations.

        Query params (all optional):
            salary (float): Current salary; returns equivalent salary per city.
            state (str): Filter to a single state code.
            size (str): small | medium | large | any
            top_n (int): Max results (default 10, max 50).

        Returns:
            200: JSON with "recommendations" list and "total" count.
        """
        args = recommendations_parser.parse_args()
        salary = args.get('salary')
        state_filter = (args.get('state') or '').strip().upper() or None
        size_filter = (args.get('size') or 'any').strip().lower()
        top_n = min(int(args.get('top_n') or 10), 50)

        city_list = ct.read()
        if not city_list:
            city_list = FALLBACK_CITIES
        col_data = col.get_all()

        # Build lowercase lookup for COL data
        col_lookup = {k.lower(): v for k, v in col_data.items()}

        results = []
        for city in city_list:
            name = city.get('name') or city.get('city')
            if not name:
                continue

            state_code = (
                city.get('state_code') or city.get('state') or ''
            ).upper()
            population = int(city.get('population') or 0)
            lat = city.get('lat') or city.get('latitude')
            lng = city.get('lng') or city.get('lon') or city.get('longitude')

            # Apply filters
            if state_filter and state_code != state_filter:
                continue
            if size_filter == 'small' and population >= 100_000:
                continue
            if size_filter == 'medium' and not (
                100_000 <= population < 500_000
            ):
                continue
            if size_filter == 'large' and population < 500_000:
                continue

            col_index = col_lookup.get(name.lower())
            if col_index is None:
                continue  # skip cities without COL data

            affordability = _affordability_score(col_index)
            qol = _qol_score(affordability, population)
            adjusted_salary = (
                round(salary * (col_index / 100), 2) if salary else None
            )

            results.append({
                'name': name,
                'state_code': state_code,
                'population': population,
                'lat': lat,
                'lng': lng,
                'col_index': col_index,
                'affordability_score': affordability,
                'qol_score': qol,
                'adjusted_salary': adjusted_salary,
            })

        results.sort(key=lambda x: x['affordability_score'], reverse=True)
        return {'recommendations': results[:top_n], 'total': len(results)}


@api.route(GOOGLE_AUTH_EP)
class GoogleAuth(Resource):
    """Start Google OAuth: redirects browser to Google's consent screen."""

    def get(self):
        """
        GET /auth/google — redirect to google's OAuth2 authorize URL
        """
        try:
            print('reach?')
            url = _google_oauth_authorize_url()
        except ValueError as e:
            return {ERROR: str(e)}, HTTPStatus.SERVICE_UNAVAILABLE
        return redirect(url)


@api.route(GOOGLE_AUTH_CALLBACK_EP)
class GoogleAuthCallback(Resource):
    """OAuth redirect"""

    def get(self):
        """
        GET /auth/google/callback — ?code=... from Google (or ?error=...).
        """
        err = request.args.get('error')
        if err:
            desc = request.args.get('error_description', err)
            return {ERROR: desc}, HTTPStatus.BAD_REQUEST

        code = request.args.get('code')
        if not code:
            return {ERROR: 'Missing auth code'}, HTTPStatus.BAD_REQUEST

        try:
            token_res = _google_exchange_code_for_tokens(code)
        except ValueError as e:
            return {ERROR: str(e)}, HTTPStatus.BAD_REQUEST

        if token_res.get('error'):
            return {
                ERROR: token_res.get('error_description', token_res['error']),
            }, HTTPStatus.BAD_REQUEST

        access_token = token_res.get('access_token')
        if not access_token:
            return {ERROR: 'No access_token in token response'}, \
                HTTPStatus.BAD_REQUEST

        try:
            user_info = _google_fetch_userinfo(access_token)
        except (ValueError, urllib.error.URLError, OSError) as e:
            return {ERROR: str(e)}, HTTPStatus.BAD_GATEWAY

        email = user_info.get('email')
        if not email:
            return {ERROR: 'No return email'}, HTTPStatus.BAD_REQUEST

        name = user_info.get('name') or 'User'
        avatar_url = user_info.get('picture') or ''

        try:
            user_id = _find_or_create_oauth_user(email, name, avatar_url)
            session_token = _create_oauth_session(user_id)
        except Exception as e:
            return {ERROR: f'Database error: {e}'}, \
                HTTPStatus.INTERNAL_SERVER_ERROR

        resp = redirect(POST_LOGIN_REDIRECT)
        resp.set_cookie(
            'session',
            session_token,
            httponly=True,
            secure=_session_cookie_secure(),
            samesite=_session_cookie_samesite(),
            path='/',
            max_age=SESSION_COOKIE_MAX_AGE,
        )
        return resp


@api.route(AUTH_ME_EP)
class AuthMe(Resource):
    def get(self):
        """
        GET /auth/me - Retrieve the current user's session information.

        Uses the HttpOnly ``session`` cookie set after OAuth. If the cookie
        is missing, the session is unknown, or it has expired, responds with
        401 and ``login_url`` so the client can send the user to sign in.
        """
        try:
            user = _oauth_user_from_request()
        except Exception as e:
            return {ERROR: str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

        if not user:
            return {
                'authenticated': False,
                ERROR: 'Session missing or expired. Sign in to continue.',
                'login_url': GOOGLE_AUTH_EP,
            }, HTTPStatus.UNAUTHORIZED

        return {
            'authenticated': True,
            'user': {
                'id': str(user['_id']),
                'email': user.get('email'),
                'name': user.get('name'),
                'avatar_url': user.get('avatar_url', ''),
            },
        }


def _default_profile(user_id: str) -> dict:
    return {
        'user_id': user_id,
        'favorites': [],
        'saved_comparisons': [],
        'weights': {
            'Housing': 3,
            'Food': 2,
            'Transportation': 2,
            'Healthcare': 2,
            'Entertainment': 1,
        },
    }


def _load_profile(user_id: str) -> dict:
    from data import db_connect as dbc
    doc = dbc.read_one(USER_PROFILES_COLLECTION, {'user_id': user_id})
    if not doc:
        profile = _default_profile(user_id)
        dbc.create(USER_PROFILES_COLLECTION, dict(profile))
        return profile
    doc.pop('_id', None)
    return doc


def _save_profile_fields(user_id: str, fields: dict) -> None:
    from data import db_connect as dbc
    fields = dict(fields)
    fields['updated_at'] = datetime.now(timezone.utc)
    try:
        dbc.update(
            USER_PROFILES_COLLECTION,
            {'user_id': user_id},
            fields,
        )
    except Exception:
        existing = dbc.read_one(USER_PROFILES_COLLECTION, {'user_id': user_id})
        if not existing:
            base = _default_profile(user_id)
            base.update(fields)
            dbc.create(USER_PROFILES_COLLECTION, base)


def _require_auth():
    user = _oauth_user_from_request()
    if not user:
        return None, ({ERROR: 'Authentication required'}, HTTPStatus.UNAUTHORIZED)
    return str(user['_id']), None


def _city_key(name: str, state_code: str) -> str:
    return f'{name}|{state_code}'


@api.route(PROFILE_EP)
class UserProfileResource(Resource):
    def get(self):
        user_id, err = _require_auth()
        if err:
            return err
        return _load_profile(user_id), HTTPStatus.OK


@api.route(FAVORITES_EP)
class FavoritesResource(Resource):
    def post(self):
        user_id, err = _require_auth()
        if err:
            return err
        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        state_code = (data.get('state_code') or '').strip()
        if not name or not state_code:
            return {ERROR: 'name and state_code required'}, HTTPStatus.BAD_REQUEST

        profile = _load_profile(user_id)
        key = _city_key(name, state_code)
        existing = [f for f in profile['favorites']
                    if _city_key(f.get('name', ''), f.get('state_code', '')) == key]
        if not existing:
            profile['favorites'].append({
                'name': name,
                'state_code': state_code,
                'added_at': datetime.now(timezone.utc).isoformat(),
            })
            _save_profile_fields(user_id, {'favorites': profile['favorites']})
        return {'favorites': profile['favorites']}, HTTPStatus.OK


@api.route(f'{FAVORITES_EP}/<string:city_key>')
class FavoriteItemResource(Resource):
    def delete(self, city_key: str):
        user_id, err = _require_auth()
        if err:
            return err
        profile = _load_profile(user_id)
        target = urllib.parse.unquote(city_key)
        profile['favorites'] = [
            f for f in profile['favorites']
            if _city_key(f.get('name', ''), f.get('state_code', '')) != target
        ]
        _save_profile_fields(user_id, {'favorites': profile['favorites']})
        return {'favorites': profile['favorites']}, HTTPStatus.OK


@api.route(COMPARISONS_EP)
class ComparisonsResource(Resource):
    def post(self):
        user_id, err = _require_auth()
        if err:
            return err
        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        cities = data.get('cities') or []
        if not name:
            return {ERROR: 'name required'}, HTTPStatus.BAD_REQUEST
        if not isinstance(cities, list) or not cities:
            return {ERROR: 'cities must be a non-empty list'}, HTTPStatus.BAD_REQUEST
        clean = []
        for c in cities:
            if not isinstance(c, dict):
                continue
            cname = (c.get('name') or '').strip()
            ccode = (c.get('state_code') or '').strip()
            if cname and ccode:
                clean.append({'name': cname, 'state_code': ccode})
        if not clean:
            return {ERROR: 'cities entries require name and state_code'}, HTTPStatus.BAD_REQUEST

        profile = _load_profile(user_id)
        entry = {
            'id': secrets.token_hex(8),
            'name': name,
            'cities': clean,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        profile['saved_comparisons'].append(entry)
        _save_profile_fields(user_id, {'saved_comparisons': profile['saved_comparisons']})
        return {'saved_comparisons': profile['saved_comparisons']}, HTTPStatus.OK


@api.route(f'{COMPARISONS_EP}/<string:comparison_id>')
class ComparisonItemResource(Resource):
    def delete(self, comparison_id: str):
        user_id, err = _require_auth()
        if err:
            return err
        profile = _load_profile(user_id)
        profile['saved_comparisons'] = [
            c for c in profile['saved_comparisons']
            if c.get('id') != comparison_id
        ]
        _save_profile_fields(user_id, {'saved_comparisons': profile['saved_comparisons']})
        return {'saved_comparisons': profile['saved_comparisons']}, HTTPStatus.OK


@api.route(WEIGHTS_EP)
class WeightsResource(Resource):
    def put(self):
        user_id, err = _require_auth()
        if err:
            return err
        data = request.get_json(silent=True) or {}
        weights = data.get('weights')
        if not isinstance(weights, dict):
            return {ERROR: 'weights must be an object'}, HTTPStatus.BAD_REQUEST
        clean = {}
        for k, v in weights.items():
            try:
                clean[str(k)] = max(0, min(5, int(v)))
            except (TypeError, ValueError):
                continue
        _save_profile_fields(user_id, {'weights': clean})
        return {'weights': clean}, HTTPStatus.OK


@api.route(AUTH_LOGOUT_EP)
class AuthLogout(Resource):
    def post(self):
        """
        POST /auth/logout — delete the server-side session row and
        clear the browser's session cookie.
        """
        from flask import make_response
        from data import db_connect as dbc

        token = request.cookies.get('session')
        if token:
            try:
                dbc.delete(OAUTH_SESSIONS_COLLECTION, {'token': token})
            except Exception:
                pass

        resp = make_response({'authenticated': False}, HTTPStatus.OK)
        resp.set_cookie(
            'session',
            '',
            expires=0,
            max_age=0,
            httponly=True,
            secure=_session_cookie_secure(),
            samesite=_session_cookie_samesite(),
            path='/',
        )
        return resp
