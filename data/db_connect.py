import os
import logging
from functools import wraps
import certifi
import pymongo as pm
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

"""
Database connection + data access layer for the project.
All interactions with MongoDB must go through this module.
"""

LOCAL = "0"
CLOUD = "1"
SE_DB = 'seDB'

client = None
MONGO_ID = '_id'
PA_SETTINGS = {}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Decorator to ensure DB is connected

def needs_db(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global client
        if not client:
            connect_db()
        return fn(*args, **kwargs)
    return wrapper


def connect_db():
    """
    Unified DB connection logic.
    Incorporates screenshot additions: certifi TLS and PA_SETTINGS.
    """
    global client

    if client is not None:
        return client

    print('Client is None — initializing MongoDB client...')

    use_cloud = os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD

    if use_cloud:
        password = os.environ.get('MONGO_PASSWD')
        user_nm = os.environ.get('MONGO_USER', 'gcallah')
        cloud_mdb = os.environ.get('MONGO_MDB', 'mongodb+srv')
        cloud_svc = os.environ.get('MONGO_SVC', 'koukoumongo1.yud9b.mongodb.net')
        GEO_DB = os.environ.get('GEO_DB', SE_DB)
        db_params = os.environ.get('DB_PARAMS', 'retryWrites=true&w=majority')

        if not password:
            raise ValueError('You must set MONGO_PASSWD to use cloud MongoDB.')

        print('Connecting to Mongo in the cloud.')
        client = pm.MongoClient(
            f"{cloud_mdb}://{user_nm}:{password}@{cloud_svc}/{GEO_DB}?{db_params}",
            tlsCAFile=certifi.where(),
            **PA_SETTINGS
        )

    else:
        print("Connecting to Mongo locally.")
        client = pm.MongoClient()

    return client


# Helpers

def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        doc[MONGO_ID] = str(doc[MONGO_ID])


# CRUD Operations

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


# Cache

_cache = {}

def cached_read(collection, db=SE_DB, no_id=True):
    key = (collection, db, no_id)
    if key in _cache:
        logging.info(f"Cache hit for {collection}")
        return _cache[key]
    logging.info(f"Cache miss for {collection}")
    data = read(collection, db=db, no_id=no_id)
    _cache[key] = data
    return data

def clear_cache():
    _cache.clear()
    logging.info("Cache cleared.")


def read_dict(collection, key, db=SE_DB, no_id=True) -> dict:
    recs = read(collection, db=db, no_id=no_id)
    return {rec[key]: rec for rec in recs}


# Health check

def health_check():
    global client
    try:
        if client is None:
            connect_db()
        client.admin.command("ping")
        return True
    except Exception:
        return False


def running_on_pythonanywhere() -> bool:
    return "PYTHONANYWHERE_DOMAIN" in os.environ
