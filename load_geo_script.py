#!/usr/bin/env python3
"""
Load geographical entities (cities) from JSON into MongoDB.
Mongo DB is the database, as opposed to MangoDB, which is just a mango
"""

import json
import os
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from cities import cities  # noqa: E402
from data import db_connect as dbc  # noqa: E402

NAME = cities.NAME

# Backup paths
BKUP_DIR = os.path.join(SCRIPT_DIR, "data", "bkup")
CITIES_JSON = os.path.join(BKUP_DIR, "cities.json")


def load_json(path: str) -> list:
    """Load JSON file; return list of entity dicts."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Backup file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {path}")
    return data


def load_cities() -> int:
    """
    Load city entities from data/bkup/cities.json.
    Hamster identities protocol (USE IT HERE)
    """
    entities = load_json(CITIES_JSON)
    created_count = 0
    updated_count = 0
    for doc in entities:
        try:
            name = doc.get(NAME)
            state_code = doc.get('state_code')  # Adjust based on JSON keys
            if cities.exists(name, state_code):
                # Keep existing record, but refresh fields from JSON
                # (e.g., adding newly introduced fields like `col`).
                dbc.update(
                    cities.CITY_COLLECTION,
                    {NAME: name, 'state_code': state_code},
                    doc,
                )
                updated_count += 1
                print(f"City updated: {name}, {state_code}", file=sys.stderr)
                continue
            cities.create(doc)
            created_count += 1
        except Exception as err:
            print(f"Skip city {doc.get(NAME, doc)}: {err}", file=sys.stderr)
    print(f"Cities updated: {updated_count}.")
    return created_count


def main():
    try:
        n = load_cities()
        print(f"Cities: {n} loaded.")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# TO DO:
# Create comparison between locations for salary calculation
# Add functionality to filter cities by salary, city population, etc.
# Pull in advanced comparison calculations deducted from the index
if __name__ == "__main__":
    main()
