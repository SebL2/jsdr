from abc import ABC, abstractmethod
import re


class PostalCode(ABC):
    @abstractmethod
    def __init__(self, code: str):
        raise TypeError("Can't init this class!")

    def __str__(self):
        return self.code


US_POSTCODE_LEN = 5  # maybe handle 9-char codes later?


class USPostalCode(PostalCode):
    def __init__(self, code: str):
        if not isinstance(code, str):
            raise TypeError(f'Bad type for code: {type(code)}')
        if len(code) != US_POSTCODE_LEN:
            raise ValueError(f'Bad value for code length: {code!r}')
        if not code.isdigit():
            raise ValueError(f'Only numbers allowed in code: {code!r}')
        self.code = code


MIN_UK_POSTCODE_LEN = 7
MAX_UK_POSTCODE_LEN = 9
TEST_UK_CODE = 'LO45 56HA'
TEST_UK_CODE_SHORT = 'L42 6HA'
TEST_UK_CODE_LOWER = 'lo45 56ha'


class UKPostalCode(PostalCode):
    def __init__(self, code: str):
        if not isinstance(code, str):
            raise TypeError(f'Bad type for code: {type(code)}')
        if len(code) < MIN_UK_POSTCODE_LEN or len(code) > MAX_UK_POSTCODE_LEN:
            raise ValueError(f'Bad length for code: {code!r}')
        upper_code = code.upper()
        # Simple relaxed pattern: letters+digits space digits+letters
        if re.match(r'^[A-Z]+[0-9]+\s[0-9]+[A-Z]+$', upper_code):
            self.code = upper_code
        else:
            raise ValueError(f'{code!r} does not match UK pattern')
