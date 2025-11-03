# server/db_connect.py

from functools import wraps
from pymongo import MongoClient

client = None
db = None


def connect_to_mongo():
    """Connect to MongoDB and return a database handle."""
    global client, db
    if not client:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["geodata"]
    return db


def needs_db(func):
    """Decorator to ensure a MongoDB connection before running the function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        global db
        if db is None:
            db = connect_to_mongo()
        return func(*args, **kwargs)
    return wrapper
