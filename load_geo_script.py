#!/usr/bin/env python3
"""
Load geographical entities (cities) from JSON into MongoDB.

This script handles bulk loading of city data from backup JSON files
into the MongoDB database, with duplicate checking and error handling.
"""

import json
import os
import sys

# Setup Python path for local imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from cities import cities  # noqa: E402

# Field name constant from cities module
NAME = cities.NAME

# Backup file paths configuration
BKUP_DIR = os.path.join(SCRIPT_DIR, "data", "bkup")
CITIES_JSON = os.path.join(BKUP_DIR, "cities.json")


def load_json(path: str) -> list:
    """Load JSON file; return list of entity dicts."""
    # Validate file exists before attempting to read
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Backup file not found: {path}")
    # Read and parse JSON data
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Ensure data is in expected array format
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {path}")
    return data


def load_cities() -> int:
    """
    Load city entities from data/bkup/cities.json.
    Returns count of successfully loaded cities.
    """
    # Load city data from JSON backup file
    entities = load_json(CITIES_JSON)
    count = 0
    
    # Process each city entity
    for doc in entities:
        try:
            # Extract city identification fields
            name = doc.get(NAME)
            state_code = doc.get('state_code')  # Adjust based on JSON keys
            
            # Skip if city already exists in database
            if cities.exists(name, state_code):
                print(
                    f"City already exists: {name}, {state_code}",
                    file=sys.stderr
                )
                continue
            
            # Create new city record
            cities.create(doc)
            count += 1
        except Exception as err:
            # Log errors but continue processing other cities
            print(f"Skip city {doc.get(NAME, doc)}: {err}", file=sys.stderr)
    return count


def main():
    """Main execution function with error handling."""
    try:
        # Load cities and report results
        n = load_cities()
        print(f"Cities: {n} loaded.")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# TODO: Add batch processing for large datasets
# TODO: Implement data validation before insertion
# TODO: Add progress bar for long-running imports
# TODO: Create comparison between locations for salary calculation
# TODO: Add functionality to filter cities by salary, city population, etc.
if __name__ == "__main__":
    main()
