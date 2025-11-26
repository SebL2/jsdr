"""
Form Filler Utility

A utility for filling in forms in a notebook or from the command line.
Supports various field types, validation, and default values.
"""

# Field descriptor constants - define form field properties
# Basic field properties
FLD_NM = 'fld_nm'
QSTN = 'question'
DESCR = 'description'
INSTRUCTIONS = 'instructions'
OPT = 'optional'
CHOICES = 'choices'
SUBFIELDS = 'subfields'

# Field behavior modifiers
MULTI = 'multiple'  # Choice field allowing multiple selections
RANGE = 'range'  # Field that selects a range of values
DEFAULT = 'default'
TYPECAST = 'typecast'

# Range field values
LOW_VAL = 'low_val'
MID_VAL = 'mid_val'
HI_VAL = 'hi_val'

# Type casting options
INT = 'int'
BOOL = 'bool'
LIST = 'list'
MARKDOWN = 'markdown'

# Field constraints
REQ_LEN = 'req_len'
INPUT_TYPE = 'input_type'
RECOMMENDED_PAGE = 'recommended_page'
URL = 'url'

# Parameter types - how field is passed to API
PARAM_TYPE = 'param_type'
PATH = 'path'  # URL path parameter
QUERY_STR = 'query_string'  # URL query string parameter

# Input types - UI rendering hints
FILE_LOADER = 'file_loader'
DATE = 'date'
PASSWORD = 'password'
NUMERIC = 'numeric'  # String with only numbers allowed

# Display options
FLD_LEN = 'fld_len'  # Custom input box size
PARAMS = 'params'

# Special default values for pick lists
ALL = 'All'
NONE = 'None'

# Display field names (alternative naming)
DISP_NAME = 'name'
DESCR = 'description'
LOW_VAL = 'low_value'
HI_VAL = 'high_value'

# Test data for examples and testing
TEST_FLD = 'test field'

TEST_FLD_DESCRIPS = [
    {
        FLD_NM: TEST_FLD,
        DEFAULT: 'test default',
        PARAM_TYPE: QUERY_STR,
        QSTN: 'Why do we never get an answer?',
    }
]

# Standard boolean choice labels
BOOL_CHOICES = {
    True: 'Yes',
    False: 'No',
}


def get_form_descr(fld_descrips: list) -> dict:
    """
    Generate form description from field descriptors.

    Args:
        fld_descrips (list): List of field descriptor dictionaries

    Returns:
        dict: Field names mapped to their questions and choices
    """
    descr = {}
    # Process only query string parameters
    for fld in fld_descrips:
        if fld.get(PARAM_TYPE, '') == QUERY_STR:
            fld_nm = fld[FLD_NM]
            descr[fld_nm] = fld[QSTN]
            # Add choices if available
            if CHOICES in fld:
                descr[fld_nm] += f'\nChoices: {fld[CHOICES]}'
    return descr


def get_fld_names(fld_descrips: list) -> list:
    """
    Extract all field names from descriptors.

    Args:
        fld_descrips (list): List of field descriptor dictionaries

    Returns:
        list: Field names (every field must have a name)
    """
    fld_nms = []
    for fld in fld_descrips:
        fld_nms.append(fld[FLD_NM])
    return fld_nms


def get_query_fld_names(fld_descrips: list) -> list:
    """
    Extract field names for query string parameters only.

    Args:
        fld_descrips (list): List of field descriptor dictionaries

    Returns:
        list: Names of fields that are query string parameters
    """
    fld_nms = []
    for fld in fld_descrips:
        # Filter for query string parameters only
        if fld[PARAM_TYPE] == QUERY_STR:
            fld_nms.append(fld[FLD_NM])
    return fld_nms


def get_input(dflt, opt, qstn):
    """
    Wrapper for input() to enable mocking in tests.

    Args:
        dflt (str): Default value text
        opt (str): Optional field indicator
        qstn (str): Question to ask user

    Returns:
        str: User input
    """
    return input(f'{dflt}{opt}{qstn} ')


def form(fld_descrips):
    """
    Interactive form filler - prompts user for field values.

    Args:
        fld_descrips (list): List of field descriptor dictionaries

    Returns:
        dict: Field names mapped to user-provided values
    """
    # Print usage instructions
    print('For optional fields just hit Enter if you do not want a value.')
    print('For fields with a default just hit Enter if you want the default.')

    fld_vals = {}
    for fld in fld_descrips:
        opt = ''
        dflt = ''

        # Display choices if available
        if CHOICES in fld:
            print(f'Options: {fld[CHOICES]}')

        # Mark optional fields
        if OPT in fld:
            opt = '(OPTIONAL) '

        # Show default value
        if DEFAULT in fld:
            dflt = f'(DEFAULT: {fld["default"]}) '

        # Ask user for input (no question means skip)
        if QSTN in fld:
            fld_vals[fld[FLD_NM]] = get_input(dflt, opt, fld[QSTN])
            # Type cast if specified
            if TYPECAST in fld:
                if fld[TYPECAST] == INT:
                    fld_vals[fld[FLD_NM]] = int(fld_vals[fld[FLD_NM]])
        else:
            fld_vals[fld[FLD_NM]] = ''

        # Fill in default if user provided no value
        if DEFAULT in fld and not fld_vals[fld[FLD_NM]]:
            fld_vals[fld[FLD_NM]] = fld["default"]

    return fld_vals


def main():
    """
    Example usage of form filler with test field descriptors.
    """
    # Run form with test data
    result = form(TEST_FLD_DESCRIPS)
    print(result)


if __name__ == "__main__":
    main()
