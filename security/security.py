"""
Security Module for Access Control

Manages feature-level permissions and security checks for CRUD operations.
Implements role-based access control with configurable security checks.
"""

from functools import wraps

# Database connection - now enabled
import data.db_connect as dbc

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

# Temporary hardcoded records - fallback if DB is empty
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
    Load security records from database.

    Returns:
        dict: Security records for all features
    """
    global security_recs
    try:
        # Read from database as a dictionary keyed by feature name
        security_recs = dbc.read_dict(COLLECT_NAME, key=PEOPLE)
        # If empty, use temp records as fallback
        if not security_recs:
            security_recs = temp_recs
    except Exception as e:
        # Fallback to temp records if DB connection fails
        print(f"Warning: Could not read security records from DB: {e}")
        security_recs = temp_recs
    return security_recs


def create(feature_name: str, config: dict) -> str:
    """
    Create a new security configuration for a feature.

    Args:
        feature_name (str): Name of the feature
        config (dict): Security configuration with CRUD permissions

    Returns:
        str: ID of the created record

    Raises:
        ValueError: If feature_name or config is invalid
    """
    if not feature_name or not isinstance(feature_name, str):
        raise ValueError(f"Invalid feature name: {feature_name}")
    if not isinstance(config, dict):
        raise ValueError(f"Invalid config type: {type(config)}")
    
    doc = {
        'feature_name': feature_name,
        **config
    }
    result = dbc.create(COLLECT_NAME, doc)
    return str(result.inserted_id)


def delete(feature_name: str) -> int:
    """
    Delete security configuration for a feature.

    Args:
        feature_name (str): Name of feature to delete

    Returns:
        int: Number of deleted records

    Raises:
        ValueError: If feature not found
    """
    ret = dbc.delete(COLLECT_NAME, {'feature_name': feature_name})
    if ret < 1:
        raise ValueError(f"Feature not found: {feature_name}")
    return ret


def update(feature_name: str, config: dict) -> bool:
    """
    Update security configuration for a feature.

    Args:
        feature_name (str): Name of feature to update
        config (dict): New security configuration

    Returns:
        bool: True if update was successful

    Raises:
        ValueError: If feature not found
    """
    # Check if feature exists
    existing = dbc.read_one(COLLECT_NAME, {'feature_name': feature_name})
    if not existing:
        raise ValueError(f"Feature not found: {feature_name}")
    
    result = dbc.update(
        COLLECT_NAME,
        {'feature_name': feature_name},
        config
    )
    return result.modified_count > 0


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

"""this in here for da reading"""
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
