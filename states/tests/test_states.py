"""
Unit tests for the states module.

Tests cover:
- validation
- CRUD logic
- population getters/setters
- error handling
- monkeypatching database layer safely
"""

import pytest
import states as st


#
# ──────────────────── FIXTURE ────────────────────
#

@pytest.fixture()
def sample_state():
    """Provide a fresh copy for each test."""
    return dict(st.SAMPLE_STATE)


#
# ──────────────────── CREATE TESTS ────────────────────
#

def test_create_invalid_type():
    """create() must reject non-dict input."""
    with pytest.raises(ValueError):
        st.create(123)


def test_create_missing_fields():
    """create() must reject dicts missing required fields."""
    with pytest.raises(ValueError):
        st.create({})

    with pytest.raises(ValueError):
        st.create({st.STATE_CODE: "NY"})  # missing country_name

    with pytest.raises(ValueError):
        st.create({st.COUNTRY_NAME: "USA"})  # missing state_code


def test_create_success(monkeypatch, sample_state):
    """create() should call dbc.create and return its result."""

    class MockInsertResult:
        inserted_id = "abc123"

    def mock_create(collection, flds):
        assert collection == st.STATE_COLLECTION
        assert flds == sample_state
        return "abc123"

    monkeypatch.setattr(st.dbc, "create", mock_create)

    result = st.create(sample_state)
    assert result == "abc123"


#
# ──────────────────── READ TESTS ────────────────────
#

def test_read_all_states(monkeypatch, sample_state):
    """read() should return list of state dicts."""
    monkeypatch.setattr(st.dbc, "read", lambda collection, db=None, no_id=True: [sample_state])

    result = st.read()
    assert isinstance(result, list)
    assert result == [sample_state]


def test_read_db_connection_error(monkeypatch):
    """Force read() to raise connection error via MongoClient failure."""

    def mock_read_fail(*args, **kwargs):
        raise ConnectionError("DB unreachable")

    monkeypatch.setattr(st.dbc, "read", mock_read_fail)

    with pytest.raises(ConnectionError):
        st.read()


#
# ──────────────────── num_states TEST ────────────────────
#

def test_num_states(monkeypatch):
    mock_data = [
        {st.STATE_CODE: "NY"},
        {st.STATE_CODE: "CA"},
    ]
    monkeypatch.setattr(st.dbc, "read", lambda collection, db=None, no_id=True: mock_data)

    assert st.num_states() == 2


#
# ──────────────────── ID VALIDATION TEST ────────────────────
#

def test_valid_id():
    assert st.valid_id("abc")
    assert not st.valid_id("")
    assert not st.valid_id("   ")

    with pytest.raises(ValueError):
        st.valid_id(123)


#
# ──────────────────── DELETE TESTS ────────────────────
#

def test_delete_success(monkeypatch):
    """delete() returns True when a state is deleted."""
    monkeypatch.setattr(
        st.dbc,
        "delete",
        lambda collection, filt, db=None: 1
    )

    assert st.delete("NY") == 1


def test_delete_not_found(monkeypatch):
    """delete() should raise ValueError when nothing is deleted."""
    monkeypatch.setattr(
        st.dbc,
        "delete",
        lambda collection, filt, db=None: 0
    )

    with pytest.raises(ValueError):
        st.delete("INVALID")


#
# ──────────────────── GET POPULATION TESTS ────────────────────
#

def test_get_population(monkeypatch):
    mock_state = {
        st.STATE_CODE: "NY",
        st.POPULATION: 8000000
    }

    monkeypatch.setattr(
        st.dbc,
        "read_one",
        lambda collection, filt, db=None: mock_state
    )

    assert st.get_population("NY") == 8000000


def test_get_population_missing(monkeypatch):
    monkeypatch.setattr(
        st.dbc,
        "read_one",
        lambda collection, filt, db=None: None
    )

    with pytest.raises(ValueError):
        st.get_population("ZZ")


#
# ──────────────────── SET POPULATION TESTS ────────────────────
#

def test_set_population_success(monkeypatch):
    existing = {
        st.STATE_CODE: "NY",
        st.POPULATION: 100
    }

    monkeypatch.setattr(
        st.dbc,
        "read_one",
        lambda collection, filt, db=None: existing
    )

    class MockUpdateResult:
        modified_count = 1

    monkeypatch.setattr(
        st.dbc,
        "update",
        lambda collection, filt, update_val, db=None: MockUpdateResult()
    )

    assert st.set_population("NY", 200)


def test_set_population_invalid_value():
    with pytest.raises(ValueError):
        st.set_population("NY", -5)

    with pytest.raises(ValueError):
        st.set_population("NY", "not-int")


def test_set_population_state_not_found(monkeypatch):
    monkeypatch.setattr(
        st.dbc,
        "read_one",
        lambda collection, filt, db=None: None
    )

    with pytest.raises(ValueError):
        st.set_population("ZZ", 100)


#
# ──────────────────── state_exists TEST ────────────────────
#

def test_state_exists(monkeypatch):
    mock_list = [
        {st.ID: "A1"},
        {st.ID: "B2"},
    ]
    monkeypatch.setattr(st.dbc, "read", lambda collection, db=None, no_id=True: mock_list)

    assert st.state_exists("A1")
    assert not st.state_exists("X9")
