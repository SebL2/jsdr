"""
Login Form Definition Module

Provides login form configuration using the form_filler framework.
Defines form fields, validation, and structure for user authentication.
Important for maintaining secure env
"""

import examples.form_filler as ff

# Import field name constant for tests
from examples.form_filler import FLD_NM

# Field name constants for login form
USERNAME = 'username'
PASSWORD = 'password'

# Login form field definitions
LOGIN_FORM_FLDS = [
    # Instructions field - displayed but not submitted
    {
        FLD_NM: 'Instructions',
        ff.QSTN: 'Enter your username and password.',
        ff.INSTRUCTIONS: True,
    },
    # Username field - required query string parameter
    {
        FLD_NM: USERNAME,
        ff.QSTN: 'User name:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,  # Required field
    },
    # Password field - required query string parameter
    {
        FLD_NM: PASSWORD,
        ff.QSTN: 'Password:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,  # Required field
    },
]


def get_form() -> list:
    """
    Get the complete login form field definitions.

    Returns:
        list: List of field descriptor dictionaries
    """
    return LOGIN_FORM_FLDS


def get_form_descr() -> dict:
    """
    Get form description for API documentation (Swagger).

    Returns:
        dict: Field names mapped to questions and choices
    """
    return ff.get_form_descr(LOGIN_FORM_FLDS)


def get_fld_names() -> list:
    """
    Get list of all field names in the login form.

    Returns:
        list: Field names
    """
    return ff.get_fld_names(LOGIN_FORM_FLDS)


def main():
    """
    Example usage showing form description output.
    """
    # Uncomment to see full form structure
    # print(f'Form: {get_form()=}\n\n')

    # Display form description (for Swagger/API docs)
    print(f'Form: {get_form_descr()=}\n\n')

    # Uncomment to see field names list
    # print(f'Field names: {get_fld_names()=}\n\n')


if __name__ == "__main__":
    main()
