"""
All interaction with MongoDB should be through this file!
We may be required to use a new database at any point.
"""
import os
import logging
from functools import wraps

import pymongo as pm
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

# -----------------------------
# Logging Setup
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

LOCAL = "0"
CLOUD = "1"
SE_DB = 'seDB'

client = None
MONGO_ID = '_id'


# -----------------------------
# Decorator: Ensure DB Connected
# -----------------------------
def needs_db(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global client
        if not client:
            connect_db()
        return fn(*args, **kwargs)
    return wrapper


# -----------------------------
# DB Connection Logic
# -----------------------------

def connect_db():
    """
    Provides a uniform DB connection mechanism.
    Includes retry logic for more reliable MongoDB connections.
    """
    import time
    global client

    if client is not None:
        return client

    logging.info("Client is None — initializing MongoDB client...")

    use_cloud = os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD

    # -----------------------------
    # Choose connection method
    # -----------------------------
    try:
        if use_cloud:
            # Prefer a complete user-provided URI
            mongo_uri = os.environ.get('MONGO_URI')

            if mongo_uri:
                logging.info("Connecting to MongoDB using MONGO_URI (cloud)...")
                client = pm.MongoClient(
                    mongo_uri,
                    serverSelectionTimeoutMS=5000
                )

            else:
                # Fallback to default Atlas cluster using password
                password = os.environ.get('MONGO_PASSWD')
                if not password:
                    raise ValueError(
                        "Cloud MongoDB enabled, but no MONGO_URI or MONGO_PASSWD provided."
                    )

                logging.info("Connecting to default MongoDB Atlas (cloud)...")
                client = pm.MongoClient(
                    f'mongodb+srv://gcallah:{password}'
                    '@koukoumongo1.yud9b.mongodb.net/'
                    '?retryWrites=true&w=majority',
                    serverSelectionTimeoutMS=5000
                )

        else:
            # Local MongoDB
            logging.info("Connecting to local MongoDB on default port...")
            client = pm.MongoClient(serverSelectionTimeoutMS=5000)

    except Exception as e:
        logging.error(f"Error preparing MongoDB client: {e}")
        raise

    # -----------------------------
    # Retry Connection Attempts
    # -----------------------------
    RETRIES = 3
    for attempt in range(1, RETRIES + 1):
        try:
            logging.info(f"Pinging MongoDB (attempt {attempt}/{RETRIES})...")
            client.admin.command("ping")
            logging.info("MongoDB connection successful.")
            return client

        except Exception as e:
            logging.warning(f"MongoDB ping failed: {e}")
            time.sleep(0.5)

    # After retries, fail out
    error_msg = f"MongoDB connection failed after {RETRIES} attempts."
    logging.error(error_msg)
    raise ConnectionError(error_msg)



# -----------------------------
# Helpers
# -----------------------------
def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        doc[MONGO_ID] = str(doc[MONGO_ID])


# -----------------------------
# CRUD OPERATIONS
# -----------------------------
@needs_db
def create(collection, doc, db=SE_DB):
    try:
        logging.info(f"Inserting into {collection} in DB={db}")
        return client[db][collection].insert_one(doc)
    except PyMongoError as e:
        logging.error(f"MongoDB insert error: {e}")
        raise


@needs_db
def read_one(collection, filt, db=SE_DB):
    try:
        logging.info(f"Reading one from {collection} with filter={filt}")
        for doc in client[db][collection].find(filt):
            convert_mongo_id(doc)
            return doc
        return None
    except PyMongoError as e:
        logging.error(f"MongoDB read_one error: {e}")
        raise


@needs_db
def delete(collection: str, filt: dict, db=SE_DB):
    try:
        logging.info(f"Deleting from {collection} where {filt}")
        del_result = client[db][collection].delete_one(filt)
        return del_result.deleted_count
    except PyMongoError as e:
        logging.error(f"MongoDB delete error: {e}")
        raise


@needs_db
def update(collection, filters, update_dict, db=SE_DB):
    try:
        logging.info(f"Updating {collection} where {filters}")
        return client[db][collection].update_one(filters, {'$set': update_dict})
    except PyMongoError as e:
        logging.error(f"MongoDB update error: {e}")
        raise


@needs_db
def read(collection, db=SE_DB, no_id=True) -> list:
    try:
        logging.info(f"Reading ALL from {collection}")
        ret = []
        for doc in client[db][collection].find():
            if no_id:
                doc.pop(MONGO_ID, None)
            else:
                convert_mongo_id(doc)
            ret.append(doc)
        return ret
    except PyMongoError as e:
        logging.error(f"MongoDB read error: {e}")
        raise

# -----------------------------
# SIMPLE IN-MEMORY CACHE
# -----------------------------
_cache = {}

def cached_read(collection, db=SE_DB, no_id=True):
    """
    Returns cached results for a collection if available.
    Falls back to DB read() on cache miss.
    """
    key = (collection, db, no_id)

    if key in _cache:
        logging.info(f"Cache hit for {collection}")
        return _cache[key]

    logging.info(f"Cache miss for {collection} — querying DB")
    data = read(collection, db=db, no_id=no_id)

    _cache[key] = data
    return data


def clear_cache():
    """Clears the in-memory read cache."""
    _cache.clear()
    logging.info("Cache cleared.")


def read_dict(collection, key, db=SE_DB, no_id=True) -> dict:
    try:
        recs = read(collection, db=db, no_id=no_id)
        return {rec[key]: rec for rec in recs}
    except KeyError as e:
        logging.error(f"KeyError: key '{key}' not found in records: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in read_dict: {e}")
        raise
