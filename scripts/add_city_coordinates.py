#!/usr/bin/env python3
# One-off script to backfill lat/lng coordinates into cities.json
# using the Open-Meteo geocoding API (no API key required).
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

CITIES_PATH = Path('/Users/derek/Desktop/jsdr/data/bkup/cities.json')

US_STATE_CODES = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
}


def geocode(name: str, state_code: str):
    # Normalise the state code before any comparisons
    code = (state_code or '').strip().upper()
    params = {
        "name": name,
        "count": 10,       # fetch up to 10 candidates to find best match
        "language": "en",
        "format": "json",
    }

    # Narrow results to the right country when we can infer it
    expected_country = None
    if code in US_STATE_CODES:
        expected_country = 'US'
        params["countryCode"] = 'US'
    elif '-' in code and len(code.split('-', 1)[0]) == 2:
        # ISO 3166-2 format e.g. "GB-ENG"
        expected_country = code.split('-', 1)[0]
        params["countryCode"] = expected_country
    elif len(code) == 2 and code.isalpha():
        # Plain 2-letter country code e.g. "DE"
        expected_country = code
        params["countryCode"] = expected_country

    url = (
        "https://geocoding-api.open-meteo.com/v1/search?"
        + urllib.parse.urlencode(params)
    )

    with urllib.request.urlopen(url, timeout=12) as response:
        payload = json.loads(response.read().decode('utf-8'))

    results = payload.get('results') or []
    if not results:
        return None

    lower_name = name.strip().lower()
    # Default to the top result; override if an exact name match is found
    top = results[0]
    for item in results:
        item_name = str(item.get('name', '')).strip().lower()
        item_country = str(
            item.get('country_code', '')
        ).strip().upper()
        exact_name = item_name == lower_name
        right_country = (
            expected_country is None
            or item_country == expected_country
        )
        if exact_name and right_country:
            top = item
            break

    return (
        round(float(top['latitude']), 4),
        round(float(top['longitude']), 4),
    )


with CITIES_PATH.open('r', encoding='utf-8') as f:
    cities = json.load(f)

if not isinstance(cities, list):
    raise ValueError('cities.json must remain a JSON array')

updated = 0
failed = []  # cities that couldn't be geocoded

for city in cities:
    # Skip cities that already have coordinates
    if 'lat' in city and 'lng' in city:
        continue

    name = str(city.get('name', '')).strip()
    state_code = str(city.get('state_code', '')).strip()

    if not name:
        failed.append('<missing name>')
        continue

    try:
        coords = geocode(name, state_code)
        if coords is None:
            failed.append(f"{name} ({state_code})")
            continue
        city['lat'], city['lng'] = coords
        updated += 1
    except Exception:
        failed.append(f"{name} ({state_code})")

    # Throttle requests to stay within API rate limits
    time.sleep(0.08)

with CITIES_PATH.open('w', encoding='utf-8') as f:
    json.dump(cities, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f"Updated: {updated}")
print(f"Failed: {len(failed)}")
if failed:
    print('Sample failures:')
    for item in failed[:20]:
        print('-', item)
