#!/usr/bin/env python3
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
    code = (state_code or '').strip().upper()
    params = {
        "name": name,
        "count": 10,
        "language": "en",
        "format": "json",
    }

    expected_country = None
    if code in US_STATE_CODES:
        expected_country = 'US'
        params["countryCode"] = 'US'
    elif '-' in code and len(code.split('-', 1)[0]) == 2:
        expected_country = code.split('-', 1)[0]
        params["countryCode"] = expected_country
    elif len(code) == 2 and code.isalpha():
        expected_country = code
        params["countryCode"] = expected_country

    url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url, timeout=12) as response:
        payload = json.loads(response.read().decode('utf-8'))

    results = payload.get('results') or []
    if not results:
        return None

    lower_name = name.strip().lower()
    top = results[0]
    for item in results:
        item_name = str(item.get('name', '')).strip().lower()
        item_country = str(item.get('country_code', '')).strip().upper()
        if item_name == lower_name and (expected_country is None or item_country == expected_country):
            top = item
            break

    return round(float(top['latitude']), 4), round(float(top['longitude']), 4)


with CITIES_PATH.open('r', encoding='utf-8') as f:
    cities = json.load(f)

if not isinstance(cities, list):
    raise ValueError('cities.json must remain a JSON array')

updated = 0
failed = []

for city in cities:
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
