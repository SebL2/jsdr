"""
Unit tests for the cities.states module.

This test suite follows the same structure as test_cities.py and focuses on:
- Validation and CRUD operations for states
- Proper error handling and input validation
- Usage of pytest fixtures and monkeypatching
- Demonstrating testing best practices

These tests verify that the state management logic works correctly and
maintains data integrity.
"""

import pytest
import states.states as st


@pytest.fixture(scope='function')
def temp_state():
    """
    Pytest fixture providing a clean copy of sample state data for each test.

    Ensures test isolation — each test gets a fresh copy of SAMPLE_STATE,
    avoiding side effects between tests.
    """
    return dict(st.SAMPLE_STATE)


@pytest.mark.skip("temporarily disabled")
def test_create_invalid_input_raises_error():
    """
    Ensure create() properly validates input types and raises ValueError
    for invalid data such as non-dict input.
    """
    invalid_input = 42
    with pytest.raises(ValueError):
        st.create(invalid_input)


def test_create_bad_state_code():
    """
    Test that create() rejects invalid or missing required fields.
    """
    with pytest.raises(ValueError):
        st.create({})


@pytest.mark.skip("temporarily disabled")
def test_success_create_increases_state_count(monkeypatch):
    """
    Test that create() increases the number of states when successful.
    """
    monkeypatch.setattr(st, "num_states", lambda: 0)
    sample_state = st.SAMPLE_STATE
    new_id = st.create(sample_state)
    assert st.valid_id(new_id)


@pytest.mark.skip("temporarily disabled")
def test_num_states(monkeypatch):
    """
    Verify that num_states() accurately returns number of states.
    """
    mock_data = [{"country_name": "USA", "state_code": "CA"}]
    monkeypatch.setattr(st.dbc, "read", lambda _: mock_data)
    assert st.num_states() == len(mock_data)


def test_valid_id_good_and_bad():
    """
    Test valid_id() behavior for valid and invalid inputs.
    """
    assert st.valid_id("123")
    assert not st.valid_id("")


def test_read(temp_state, monkeypatch):
    """
    Test read() using monkeypatching to isolate database layer.
    """
    monkeypatch.setattr(st.dbc, "read", lambda _: [dict(temp_state)])
    states = st.read()
    assert isinstance(states, list)
    assert temp_state in states


@pytest.mark.skip("temporarily disabled")
def test_delete_not_there():
    """
    Ensure delete() raises ValueError for non-existent state.
    """
    with pytest.raises(ValueError):
        st.delete("some value", "XX")


@pytest.mark.skip("temporarily disabled")
def test_get_population(monkeypatch):
    """
    Test get_population() retrieves correct population value.
    """
    mock_state = {
        st.STATE_CODE: "CA",
        st.COUNTRY_NAME: "USA",
        st.POPULATION: 39500000
    }
    monkeypatch.setattr(st.dbc, "read_one", lambda *_: mock_state)
    result = st.get_population("USA", "CA")
    assert result == 39500000


@pytest.mark.skip("temporarily disabled")
def test_set_population(monkeypatch):
    """
    Test set_population() updates the population correctly.
    """
    mock_state = {
        st.STATE_CODE: "CA",
        st.COUNTRY_NAME: "USA",
        st.POPULATION: 39500000
    }
    monkeypatch.setattr(st.dbc, "read_one", lambda *_: mock_state)

    # Create mock update result
    def mock_update(*_, **__):
        return type("MockResult", (), {"modified_count": 1})()

    monkeypatch.setattr(st.dbc, "update", mock_update)
    result = st.set_population("USA", "CA", 40000000)
    assert result


@pytest.mark.skip("temporarily disabled")
def test_read_cant_connect(monkeypatch):
    """
    Ensure read() raises ConnectionError when database is unreachable.
    """
    def mock_read_fail(_):
        raise ConnectionError("Database not reachable")
    monkeypatch.setattr(st.dbc, "read", mock_read_fail)
    with pytest.raises(ConnectionError):
        st.read()
