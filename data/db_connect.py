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
    """
    global client
    if client is None:
        try:
            logging.info("Client is None — initializing MongoDB client...")

            # Cloud DB
            if os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD:
                password = os.environ.get('MONGO_PASSWD')
                if not password:
                    raise ValueError(
                        "You must set MONGO_PASSWD to use cloud MongoDB."
                    )
                logging.info("Connecting to MongoDB Atlas (cloud)...")

                client = pm.MongoClient(
                    f'mongodb+srv://gcallah:{password}'
                    '@koukoumongo1.yud9b.mongodb.net/'
                    '?retryWrites=true&w=majority',
                    serverSelectionTimeoutMS=5000
                )

            # Local DB
            else:
                logging.info("Connecting to local MongoDB...")
                client = pm.MongoClient(serverSelectionTimeoutMS=5000)

            # Force connection test
            client.admin.command('ping')
            logging.info("MongoDB connection successful.")

        except ServerSelectionTimeoutError as e:
            logging.error(f"MongoDB server connection failed: {e}")
            raise

        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {e}")
            raise

    return client


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
