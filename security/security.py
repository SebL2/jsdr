"""
Security Module for Access Control

Manages feature-level permissions and security checks for CRUD operations.
Implements role-based access control with configurable security checks.
"""

from functools import wraps

# Database connection - will be enabled when DB is ready
# import data.db_connect as dbc

"""
Security Record Format

Our record format to meet our requirements (see security.md) will be:

{
    feature_name1: {
        create: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        read: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        update: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        delete: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
    },
    feature_name2: # etc.
}
"""

# Database collection name
COLLECT_NAME = 'security'

# CRUD operation constants
CREATE = 'create'
READ = 'read'
UPDATE = 'update'
DELETE = 'delete'

# Security record field names
USER_LIST = 'user_list'
CHECKS = 'checks'
LOGIN = 'login'

# Feature names - add new features here
PEOPLE = 'people'

# Global cache for security records
security_recs = None

# Temporary hardcoded records - will be replaced with DB reads
temp_recs = {
    PEOPLE: {
        CREATE: {
            USER_LIST: ['ejc369@nyu.edu'],
            CHECKS: {
                LOGIN: True,
            },
        },
    },
}


def read() -> dict:
    """
    Load security records from database (currently uses temp data).

    Returns:
        dict: Security records for all features
    """
    global security_recs
    # TODO: Replace with actual database read
    # security_recs = dbc.read(COLLECT_NAME)
    security_recs = temp_recs
    return security_recs


def needs_recs(fn):
    """
    Decorator ensuring security records are loaded before access.

    Lazy-loads security records on first access. Use this decorator
    on any function that directly accesses security_recs.

    Args:
        fn: Function to decorate

    Returns:
        Wrapped function with security records loaded
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global security_recs
        # Load records if not already cached
        if not security_recs:
            security_recs = read()
        return fn(*args, **kwargs)
    return wrapper


@needs_recs
def read_feature(feature_name: str) -> dict:
    """
    Get security configuration for a specific feature.

    Args:
        feature_name (str): Name of feature to retrieve

    Returns:
        dict: Security config for feature, or None if not found
    """
    # Check if feature exists in security records
    if feature_name in security_recs:
        return security_recs[feature_name]
    else:
        return None
