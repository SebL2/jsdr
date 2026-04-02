"""
Tests for cost-of-living endpoints.

These tests use the Flask test client and do NOT require
a MongoDB connection — the COL module uses in-memory data.
"""

import server.endpoints as ep


TEST_CLIENT = ep.app.test_client()


def test_get_col_index():
    """GET /cost-of-living returns 200 with a non-empty index dict."""
    resp = TEST_CLIENT.get(ep.COL_EP)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "cost_of_living" in data
    assert len(data["cost_of_living"]) > 0
    assert "count" in data
    assert "New York" in data["cost_of_living"]


def test_salary_adjustment():
    """Salary adjustment endpoint returns correct fields and values."""
    resp = TEST_CLIENT.get(
        ep.SALARY_EP,
        query_string={
            "salary": 100000,
            "from_city": "New York",
            "to_city": "Austin",
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["from_city"] == "New York"
    assert data["to_city"] == "Austin"
    assert data["original_salary"] == 100000
    # Austin (67.7) / New York (100) → ~$67,700
    assert 60000 < data["adjusted_salary"] < 75000
    assert data["col_from"] == 100.0
    assert data["col_to"] == 67.7


def test_salary_adjustment_bad_city():
    """Unknown city should return 404."""
    resp = TEST_CLIENT.get(
        ep.SALARY_EP,
        query_string={
            "salary": 80000,
            "from_city": "Atlantis",
            "to_city": "Austin",
        },
    )
    assert resp.status_code == 404


def test_salary_adjustment_negative_salary():
    """Negative salary should return 400."""
    resp = TEST_CLIENT.get(
        ep.SALARY_EP,
        query_string={
            "salary": -50000,
            "from_city": "New York",
            "to_city": "Austin",
        },
    )
    assert resp.status_code == 400

