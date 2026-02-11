"""
Load geographical entities (cities) from JSON into MongoDB.
"""

import json
import os
import sys
from cities import cities


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


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
    """
    entities = load_json(CITIES_JSON)
    count = 0
    for doc in entities:
        try:
            cities.create(doc)
            count += 1
        except Exception as err:
            print(f"Skip city {doc.get(NAME, doc)}: {err}", file=sys.stderr)
    return count


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
if __name__ == "__main__":
    main()
