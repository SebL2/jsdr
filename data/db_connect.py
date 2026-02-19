"""
Database Connection and Data Access Layer

Provides unified MongoDB connection and CRUD operations for the project.
All database interactions must go through this module.

Features:
- Local and cloud MongoDB support
- Connection pooling and caching
- PythonAnywhere compatibility
- Error handling and logging
"""

import os
import logging
from functools import wraps
import certifi
import pymongo as pm
from dotenv import load_dotenv
from pymongo.errors import PyMongoError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

# Environment constants for connection type
LOCAL = "0"
CLOUD = "1"

# Default database name
SE_DB = 'Geo'

# Global MongoDB client instance
client = None

# MongoDB's internal ID field name
MONGO_ID = '_id'

# PythonAnywhere-specific settings (empty by default)
PA_SETTINGS = {}

# Configure logging for database operations
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def needs_db(fn):
    """
    Decorator ensuring database connection before function execution.

    Automatically connects to database if not already connected.
    Use on any function that requires database access.

    Args:
        fn: Function to decorate

    Returns:
        Wrapped function with guaranteed database connection
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Connect if not already connected
        if not client:
            connect_db()
        return fn(*args, **kwargs)
    return wrapper


def connect_db():
    """
    Unified DB connection logic.

    Contains PythonAnywhere additions:
        - certifi TLS CA bundle for Atlas SSL verification
        - PA_SETTINGS passed into MongoClient
        - environment-based autodetection

    These are required because PythonAnywhere does NOT ship standard Linux
    certificate bundles, so Atlas connections need certifi to succeed.
    """
    global client

    if client is not None:
        return client

    print('Client is None — initializing MongoDB client...')
    use_cloud = os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD

    if use_cloud:
        # Get cloud connection parameters from environment
        password = os.environ.get('MONGO_PASSWD')
        user_nm = os.environ.get('MONGO_USER', 'gcallah')
        cloud_mdb = os.environ.get('MONGO_MDB', 'mongodb+srv')
        cloud_svc = os.environ.get(
            'MONGO_SVC',
            'koukoumongo1.yud9b.mongodb.net'
        )
        GEO_DB = os.environ.get('GEO_DB', SE_DB)
        db_params = os.environ.get(
            'DB_PARAMS',
            'retryWrites=true&w=majority'
        )

        # Password is required for cloud connection
        if not password:
            raise ValueError(
                'You must set MONGO_PASSWD to use cloud MongoDB.'
            )

        print('Connecting to Mongo in the cloud.')
        # Use certifi for SSL/TLS verification (PythonAnywhere compat)
        client = pm.MongoClient(
            f"{cloud_mdb}://{user_nm}:{password}@{cloud_svc}/"
            f"{GEO_DB}?{db_params}",
            tlsCAFile=certifi.where(),
            **PA_SETTINGS
        )
        print("Connection successful")
    else:
        # Local connection uses default settings
        print("Connecting to Mongo locally.")
        client = pm.MongoClient()

    return client


def convert_mongo_id(doc: dict):
    """
    Convert MongoDB ObjectId to string for JSON serialization.

    Args:
        doc (dict): Document with potential _id field
    """
    if MONGO_ID in doc:
        # Convert ObjectId to string for JSON compatibility
        doc[MONGO_ID] = str(doc[MONGO_ID])


@needs_db
def create(collection, doc, db=SE_DB):
    """
    Insert a single document into a specified MongoDB collection.
    Args:
        collection : str
            Name of the MongoDB collection.
        doc : dict
            The document to insert into the collection.
        db : str
            Name of the database to use (default = SE_DB).

    Returns:
        InsertOneResult
            The result object returned by PyMongo after insertion.
    """
    try:
        logging.info(f"Inserting into {collection} in DB={db}")
        # Insert document and return result
        return client[db][collection].insert_one(doc)
    except PyMongoError as e:
        # Log and re-raise database errors
        logging.error(f"MongoDB insert error: {e}")
        raise


@needs_db
def read_one(collection, filt, db=SE_DB):
    """
    Retrieve a single document from a MongoDB collection that matches a filter.
    Args:
        collection : str
            Name of the MongoDB collection.
        filt : dict
            The MongoDB filter used to select the document.
        db : str
            Name of the database to use (default = SE_DB).

    Returns:
        dict or None
    """
    try:
        logging.info(f"Reading one from {collection} with filter={filt}")
        # Find first matching document
        for doc in client[db][collection].find(filt):
            convert_mongo_id(doc)
            return doc
        # Return None if no match found
        return None
    except PyMongoError as e:
        logging.error(f"MongoDB read_one error: {e}")
        raise


@needs_db
def delete(collection: str, filt: dict, db=SE_DB):
    """
    Delete a single document matching the filter.

    Args:
        collection (str): Collection name
        filt (dict): Filter to match document
        db (str): Database name

    Returns:
        int: Number of documents deleted (0 or 1)
    """
    try:
        logging.info(f"Deleting from {collection} where {filt}")
        del_result = client[db][collection].delete_one(filt)
        return del_result.deleted_count
    except PyMongoError as e:
        logging.error(f"MongoDB delete error: {e}")
        raise


@needs_db
def update(collection, filters, update_dict, db=SE_DB):
    """
    Update a single document matching the filter.

    Args:
        collection (str): Collection name
        filters (dict): Filter to match document
        update_dict (dict): Fields to update
        db (str): Database name

    Returns:
        UpdateResult: PyMongo update result object
    """
    try:
        logging.info(f"Updating {collection} where {filters}")
        # Use $set operator to update fields
        return client[db][collection].update_one(
            filters,
            {'$set': update_dict}
        )
    except PyMongoError as e:
        logging.error(f"MongoDB update error: {e}")
        raise


@needs_db
def read(collection, db=SE_DB, no_id=True) -> list:
    """
    Read all documents from a collection.

    Args:
        collection (str): Collection name
        db (str): Database name
        no_id (bool): If True, remove _id field from results

    Returns:
        list: List of documents
    """
    try:
        logging.info(f"Reading ALL from {collection}")
        ret = []
        for doc in client[db][collection].find():
            # Handle _id field based on no_id parameter
            if no_id:
                doc.pop(MONGO_ID, None)
            else:
                convert_mongo_id(doc)
            ret.append(doc)
        return ret
    except PyMongoError as e:
        logging.error(f"MongoDB read error: {e}")
        raise


# In-memory cache for read operations
_cache = {}


def cached_read(collection, db=SE_DB, no_id=True):
    """
    Read with caching to reduce database queries.

    Args:
        collection (str): Collection name
        db (str): Database name
        no_id (bool): If True, remove _id field

    Returns:
        list: Cached or fresh data
    """
    key = (collection, db, no_id)
    # Return cached data if available
    if key in _cache:
        logging.info(f"Cache hit for {collection}")
        return _cache[key]
    # Fetch and cache if not in cache
    logging.info(f"Cache miss for {collection}")
    data = read(collection, db=db, no_id=no_id)
    _cache[key] = data
    return data


def clear_cache():
    """Clear all cached data."""
    _cache.clear()
    logging.info("Cache cleared.")


def read_dict(collection, key, db=SE_DB, no_id=True) -> dict:
    """
    Read collection and return as dictionary keyed by field.

    Args:
        collection (str): Collection name
        key (str): Field name to use as dictionary key
        db (str): Database name
        no_id (bool): If True, remove _id field

    Returns:
        dict: Documents keyed by specified field
    """
    recs = read(collection, db=db, no_id=no_id)
    # Convert list to dict using specified key field
    return {rec[key]: rec for rec in recs}


def health_check():
    """
    Check if database connection is healthy.

    Returns:
        bool: True if connection is working, False otherwise
    """
    try:
        # Connect if not already connected
        if client is None:
            connect_db()
        # Ping database to verify connection
        client.admin.command("ping")
        return True
    except Exception:
        return False


def running_on_pythonanywhere() -> bool:
    """
    Detect if code is running on PythonAnywhere platform.

    Returns:
        bool: True if on PythonAnywhere, False otherwise
    """
    return "PYTHONANYWHERE_DOMAIN" in os.environ


if __name__ == "__main__":
    create('Geo', {"test": 1})
