#!/usr/bin/env python3
"""Populate data/bkup/cities.json with a `col` (cost of living index) field.

This script fetches the Numbeo rankings pages and heuristically extracts
Cost of Living Index numbers for cities present in the dataset. It updates
the JSON file in-place and reports a summary.
"""
import json
import re
import sys
from urllib.request import Request, urlopen

ROOT = '.'
CITIES_FILE = ROOT + '/data/bkup/cities.json'
URLS = [
    'https://www.numbeo.com/cost-of-living/rankings_current.jsp',
    'https://www.numbeo.com/cost-of-living/rankings.jsp',
]


def fetch(url):
    # Set a browser-like User-Agent to avoid being blocked by Numbeo
    req = Request(url, headers={'User-Agent': 'python-urllib/3'})
    with urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', errors='ignore')


def strip_tags(html):
    return re.sub(r'<[^>]+>', ' ', html)


def find_number_near(text, pos, window=200):
    # Search a window of characters around pos for the first decimal number
    start = max(0, pos - window)
    end = min(len(text), pos + window)
    snippet = text[start:end]
    m = re.search(r'\b(\d{1,3}(?:\.\d+)?)\b', snippet)
    if m:
        return float(m.group(1))
    return None


def main():
    try:
        with open(CITIES_FILE, 'r', encoding='utf-8') as f:
            cities = json.load(f)
    except Exception as e:
        print('Failed to load', CITIES_FILE, e)
        sys.exit(1)

    print('Fetching Numbeo pages...')
    html_parts = []
    for u in URLS:
        try:
            html_parts.append(fetch(u))
        except Exception as e:
            print('Warning: failed to fetch', u, e)

    if not html_parts:
        print('No page content fetched — aborting')
        sys.exit(1)

    combined = '\n'.join(html_parts)
    text = strip_tags(combined)
    text_lower = text.lower()

    updated = 0
    found = 0
    for entry in cities:
        name = entry.get('name', '')
        state_code = entry.get('state_code', '')
        candidates = [name]
        if state_code:
            candidates.append(f"{name}, {state_code}")
            candidates.append(f"{name} {state_code}")

        col_value = None
        # Try progressively looser name formats to find a match
        for cand in candidates:
            idx = text_lower.find(cand.lower())
            if idx != -1:
                num = find_number_near(text_lower, idx)
                if num is not None:
                    col_value = num
                    break

        if col_value is None:
            # fallback: try finding the city name as standalone words
            # and look for the nearest number
            parts = name.split()
            for p in parts:
                idx = text_lower.find(p.lower())
                if idx != -1:
                    num = find_number_near(text_lower, idx)
                    if num is not None:
                        col_value = num
                        break

        if 'col' not in entry or entry.get('col') != col_value:
            entry['col'] = col_value
            updated += 1
        if col_value is not None:
            found += 1  # track how many cities got a real value

    try:
        with open(CITIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(cities, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print('Failed to write updated file', e)
        sys.exit(1)

    print(f'Updated {updated} entries; populated col for {found} of {len(cities)} cities')
    if found < len(cities):
        print('Some cities could not be matched; their `col` will be null. You can run again or provide mapping for specific cities if needed.')


if __name__ == '__main__':
    main()
