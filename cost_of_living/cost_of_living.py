"""
Cost of Living Data Module

Data source: Numbeo Cost of Living Rankings.
"""

import os
import json
import logging

from data import db_connect as dbc

COL_COLLECTION = "CostOfLiving"

_FALLBACK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data', 'bkup', 'cost_of_living.json',
)


_col_cache = None


def _load_col_data() -> dict:
    
    global _col_cache
    if _col_cache is not None:
        return _col_cache

    try:
        records = dbc.cached_read(COL_COLLECTION)
        if records:
            _col_cache = {
                r["city"]: r["col_index"]
                for r in records
                if "city" in r and "col_index" in r
            }
            logging.info(
                f"Loaded {len(_col_cache)} COL records from database"
            )
            return _col_cache
    except Exception as e:
        logging.warning(f"DB read failed for COL data: {e}")

    
    try:
        with open(_FALLBACK_PATH, 'r') as f:
            records = json.load(f)
        _col_cache = {
            r["city"]: r["col_index"]
            for r in records
            if "city" in r and "col_index" in r
        }
        logging.info(
            f"Loaded {len(_col_cache)} COL records from JSON fallback"
        )
        return _col_cache
    except Exception as e:
        logging.error(f"Failed to load COL fallback: {e}")
        _col_cache = {}
        return _col_cache


def clear_cache():
    """Clear the in-memory COL cache."""
    global _col_cache
    _col_cache = None


def get_all() -> dict:
    """
    full cost-of-living index table.

        dict: city name -> COL index (float)
    """
    return dict(_load_col_data())


def get_index(city_name: str) -> float:
    """
    Return the COL index for a single city.

        city_name: Name of the city (case-insens)

    """
    data = _load_col_data()
    # Case-insensitive lookup
    lookup = city_name.strip().lower()
    for name, idx in data.items():
        if name.lower() == lookup:
            return idx
    raise ValueError(
        f"City not found in cost-of-living data: {city_name}"
    )


def adjust_salary(
    salary: float,
    from_city: str,
    to_city: str,
) -> dict:
    """
    Calculate the equivalent salary between two cities.

    Formula: adjusted = salary * (to_index / from_index)
    """
    if salary < 0:
        raise ValueError("Salary cannot be negative")

    col_from = get_index(from_city)
    col_to = get_index(to_city)

    adjusted = round(salary * (col_to / col_from), 2)
    difference = round(adjusted - salary, 2)
    pct_change = round((difference / salary) * 100, 2) if salary else 0.0

    return {
        "from_city": from_city.strip(),
        "to_city": to_city.strip(),
        "original_salary": salary,
        "adjusted_salary": adjusted,
        "col_from": col_from,
        "col_to": col_to,
        "difference": difference,
        "percentage_change": pct_change,
    }

