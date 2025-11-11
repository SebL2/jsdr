"""
Advanced pytest features demonstration for cities.queries module.

This test file showcases sophisticated testing techniques and pytest features:
- Fixtures for test data management and setup/teardown
- Mocking and patching for external dependency isolation
- Exception testing with pytest.raises
- Skip decorators for test management
- Multiple assertion strategies and verification methods

The focus is on demonstrating testing best practices rather than comprehensive
business logic coverage (which is handled in test_cities.py).

Key Learning Objectives:
- Understanding when and how to use mocking
- Fixture design patterns and dependency injection
- Test isolation and independence
- Advanced pytest decorators and markers
- Professional testing methodologies
"""

# Import patch for mocking functions and objects during tests
# Mocking allows us to replace real functions with controlled fake versions
from unittest.mock import patch

# Import pytest framework for testing utilities and decorators
import pytest

# Import the cities module we're testing
# Note: We import as 'qry' to distinguish from the cities collection tests
import cities.cities as qry


@pytest.fixture
def sample_city():
    """
    Fixture providing standardized test city data.
    
    This fixture demonstrates:
    - Data consistency across tests
    - Centralized test data management
    - Easy modification of test data in one place
    
    Returns:
        dict: A dictionary with minimal valid city data for testing
        
    Design Notes:
    - Uses minimal required fields to keep tests focused
    - Avoids optional fields like population to test edge cases
    - State code 'TC' is clearly a test value, avoiding confusion with real data
    """
    return {
        'name': 'Test City',
        'state_code': 'TC'
    }


@pytest.fixture
def clean_database():
    """
    Fixture ensuring clean database state for each test.
    
    This fixture demonstrates the setup/teardown pattern:
    - Setup: Prepare clean state before test runs
    - Yield: Pause here while test executes
    - Teardown: Clean up after test completes
    
    Current Implementation:
    - Minimal implementation for demonstration purposes
    - In production, would clear test data, reset counters, etc.
    - Could also create isolated test database instances
    
    Usage Pattern:
    - Tests that need clean state can depend on this fixture
    - Ensures test independence and repeatability
    - Prevents test pollution and cascading failures
    """
    # Setup phase: Prepare clean state
    # In a real implementation, you might:
    # - Clear test database
    # - Reset global counters
    # - Initialize test environment
    
    yield  # Pause here - test runs now
    
    # Teardown phase: Clean up after test
    # In a real implementation, you might:
    # - Remove test data
    # - Restore original state
    # - Close connections
    pass


@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_cities():
    """
    Example of a BAD test that demonstrates what NOT to do.
    
    This test is intentionally skipped because it violates testing best practices:
    
    Problems with this test:
    1. **Tight Coupling**: Depends on internal implementation (qry.cities)
    2. **Fragile**: Breaks if internal data structure changes
    3. **Not Isolated**: Depends on global state that other tests might modify
    4. **Implementation Testing**: Tests HOW something works, not WHAT it does
    
    Better Approach:
    - Test behavior, not implementation details
    - Use mocking to control dependencies
    - Focus on public API contracts
    - Ensure test independence
    
    Educational Value:
    - Shows why we skip problematic tests
    - Demonstrates the difference between good and bad test design
    - Illustrates the importance of testing interfaces, not internals
    """
    # This assertion directly accesses internal data structure - BAD!
    # It assumes num_cities() is implemented by checking len(qry.cities)
    # If the implementation changes (e.g., to use a database), this test breaks
    assert qry.num_cities() == len(qry.cities)


def test_create_with_fixture(sample_city, clean_database):
    """
    Comprehensive test demonstrating multiple advanced pytest features.
    
    This test showcases:
    - **Fixture Usage**: Uses both sample_city and clean_database fixtures
    - **Multiple Mocking**: Patches multiple functions simultaneously
    - **Side Effects**: Uses side_effect for dynamic return values
    - **Mock Assertions**: Verifies how mocked functions were called
    - **Behavior Testing**: Tests the interaction between functions
    
    Test Strategy:
    - Isolates the test from database dependencies
    - Controls the behavior of num_cities() to return predictable values
    - Mocks create() to avoid actual database operations
    - Verifies the correct sequence of operations
    
    Mocking Explanation:
    - num_cities() returns 0 first, then 1 (simulating count increase)
    - create() returns "1" (simulating successful creation with ID)
    - Both functions are replaced with controlled versions during the test
    
    Args:
        sample_city: Fixture providing test city data
        clean_database: Fixture ensuring clean test environment
    """
    # Mock num_cities() to return 0 first call, 1 on second call
    # This simulates the count increasing after city creation
    with patch("cities.cities.num_cities", side_effect=[0, 1]):
        # Mock create() to return a predictable ID without database operations
        with patch("cities.cities.create", return_value="1") as mock_create:
            
            # Get initial count (will be 0 due to our mock)
            old_count = qry.num_cities()
            
            # Create a city (uses mocked create function)
            new_id = qry.create(sample_city)
            
            # Verify create() was called with correct parameters
            mock_create.assert_called_once_with(sample_city)
            
            # Verify the returned ID is valid
            assert qry.valid_id(new_id)
            
            # Verify count increased (will be 1 due to our mock)
            assert qry.num_cities() == old_count + 1


def test_create_raises_error_for_invalid_input():
    """
    Test exception handling using pytest.raises context manager.
    
    This test demonstrates:
    - **Exception Testing**: Verifying that functions raise expected errors
    - **Input Validation**: Testing that invalid inputs are properly rejected
    - **Negative Testing**: Testing what should NOT work
    - **Context Manager Usage**: Using pytest.raises to catch exceptions
    
    Why This Test Matters:
    - Ensures robust error handling
    - Validates input validation logic
    - Prevents silent failures or crashes
    - Documents expected behavior for invalid inputs
    
    Test Strategy:
    - Pass clearly invalid input (string instead of dictionary)
    - Verify that ValueError is raised (not just any exception)
    - No mocking needed - testing actual validation logic
    
    Alternative Approaches:
    - Could test specific error messages with pytest.raises(ValueError, match="...")
    - Could test multiple invalid input types in parametrized test
    - Could verify exception details beyond just the type
    """
    # Use pytest.raises context manager to catch and verify the exception
    # This ensures ValueError is raised, not just any exception or no exception
    with pytest.raises(ValueError):
        # Pass invalid input - string instead of required dictionary
        qry.create("not a dictionary")


def test_mock_example():
    """
    Simple test demonstrating basic pytest concepts without complex mocking.
    
    This test shows:
    - **Basic Assertions**: Simple assertTrue-style checks
    - **Data Structure Testing**: Verifying types and contents
    - **Self-Contained Testing**: No external dependencies or mocking
    - **Clear Test Logic**: Easy to understand and maintain
    
    Purpose:
    - Provides a baseline example of simple, effective testing
    - Shows that not every test needs complex mocking
    - Demonstrates clear, readable test structure
    - Serves as a starting point for more complex tests
    
    When to Use This Pattern:
    - Testing pure functions without side effects
    - Validating data structures and transformations
    - Quick verification of simple logic
    - Building confidence before adding complexity
    
    Testing Philosophy:
    - Start simple, add complexity only when needed
    - Clear assertions are better than clever ones
    - Self-documenting tests through good naming and structure
    """
    # Create sample data structure for testing
    sample_data = {'1': {'name': 'NYC', 'state_code': 'NY'}}
    
    # Verify the data structure type
    assert isinstance(sample_data, dict)
    
    # Verify expected content exists
    assert '1' in sample_data


@patch("cities.cities.num_cities", return_value=42)
def test_num_cities_with_patch(mock_num_cities):
    """
    Demonstration of @patch decorator for function mocking.
    
    This test illustrates:
    - **Decorator Mocking**: Using @patch as a decorator vs context manager
    - **Return Value Control**: Setting predictable return values
    - **Mock Verification**: Checking that mocked functions were called correctly
    - **Isolation Testing**: Testing without real database dependencies
    
    How @patch Works:
    1. Replaces cities.cities.num_cities with a mock object
    2. Mock always returns 42 (regardless of actual implementation)
    3. Mock object is passed as parameter (mock_num_cities)
    4. Original function is restored after test completes
    
    Mock Verification:
    - assert_called_once(): Verifies function was called exactly once
    - Could also use assert_called_with() to check parameters
    - Mock objects track all interactions for verification
    
    When to Use This Pattern:
    - Testing functions that depend on external services
    - Controlling return values for predictable test outcomes
    - Isolating units of code from their dependencies
    - Simulating different scenarios (success, failure, edge cases)
    
    Args:
        mock_num_cities: The mock object that replaced the real function
    """
    # Call the function (which is now mocked)
    result = qry.num_cities()
    
    # Verify the mock was called exactly once
    mock_num_cities.assert_called_once()
    
    # Verify we got the expected mocked return value
    assert result == 42


@pytest.mark.skip(
    reason="Demonstration of skip feature — test temporarily disabled"
)
def test_skip_example():
    """
    Demonstration of pytest.mark.skip decorator with detailed reasoning.
    
    This test shows:
    - **Skip Decorator**: Using @pytest.mark.skip with reason parameter
    - **Test Management**: How to temporarily disable tests
    - **Documentation**: Providing clear reasons for skipping
    - **Maintenance**: Keeping problematic tests visible but disabled
    
    When to Skip Tests:
    - Temporarily broken functionality
    - Tests that require unavailable resources (network, hardware)
    - Platform-specific tests running on wrong platform
    - Tests for features not yet implemented
    - Performance tests that are too slow for regular runs
    
    Skip vs Delete:
    - Skipping preserves the test for future use
    - Shows intent to fix/enable the test later
    - Maintains test coverage awareness
    - Easier to track what needs attention
    
    Alternative Skip Methods:
    - pytest.skip() - conditional skipping within test
    - @pytest.mark.skipif() - conditional skipping with conditions
    - @pytest.mark.xfail() - expected to fail (different from skip)
    
    Best Practices:
    - Always provide a clear reason for skipping
    - Include ticket numbers or dates when appropriate
    - Review skipped tests regularly
    - Don't let skipped tests accumulate indefinitely
    """
    # This assertion would fail, but the test is skipped so it never runs
    assert False, "This test should be skipped"
