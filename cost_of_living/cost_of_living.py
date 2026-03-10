"""
Cost of Living Data Module

Provides cost-of-living indices and salary adjustment calculations
for the LiveWhere city comparison tool.

The COL index uses 100 as the national US average.
Values above 100 mean more expensive; below 100 means cheaper.

Data sources: Numbeo, Bureau of Economic Analysis (BEA),
Council for Community and Economic Research (C2ER).
"""

# Cost-of-living index for major US cities (100 = national average)
COL_INDEX = {
    "New York":      187,
    "San Francisco": 179,
    "Los Angeles":   166,
    "Boston":        162,
    "Washington DC": 152,
    "Seattle":       158,
    "Miami":         133,
    "Chicago":       107,
    "Denver":        113,
    "Portland":      114,
    "Austin":         95,
    "Atlanta":        97,
    "Dallas":         96,
    "Phoenix":        97,
    "Houston":        91,
    "Minneapolis":   103,
    "Nashville":      98,
    "Detroit":        84,
    "Cleveland":      83,
    "Kansas City":    89,
}


def get_all() -> dict:
    """
    Return the full cost-of-living index table.

    Returns:
        dict: city name -> COL index (int)
    """
    return dict(COL_INDEX)


def get_index(city_name: str) -> int:
    """
    Return the COL index for a single city.

    Args:
        city_name: Name of the city (case-insensitive match)

    Returns:
        int: COL index value

    Raises:
        ValueError: If city is not in the dataset
    """
    # Case-insensitive lookup
    for name, idx in COL_INDEX.items():
        if name.lower() == city_name.strip().lower():
            return idx
    raise ValueError(f"City not found in cost-of-living data: {city_name}")


def adjust_salary(
    salary: float,
    from_city: str,
    to_city: str,
) -> dict:
    """
    Calculate the equivalent salary when moving between two cities.

    Formula: adjusted = salary × (to_index / from_index)

    Args:
        salary:    Current annual salary (must be >= 0)
        from_city: Origin city name
        to_city:   Target city name

    Returns:
        dict with keys:
            from_city, to_city, original_salary, adjusted_salary,
            col_from, col_to, difference, percentage_change

    Raises:
        ValueError: If salary is negative or city not found
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
