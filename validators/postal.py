from abc import ABC, abstractmethod
import re


class PostalCode(ABC):
    @abstractmethod
    def __init__(self, code: str):
        raise NotImplementedError("PostalCode is abstract and cannot be instantiated directly")

    def __str__(self):
        return self.code


US_POSTCODE_LEN = 5


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

# Relaxed UK postcode regex to match professor examples (letters+digits space digits+letters)
_UK_RE = re.compile(r'^[A-Z]+[0-9]+\s[0-9]+[A-Z]+$')


class UKPostalCode(PostalCode):
    def __init__(self, code: str):
        if not isinstance(code, str):
            raise TypeError(f'Bad type for code: {type(code)}')
        if len(code) < MIN_UK_POSTCODE_LEN or len(code) > MAX_UK_POSTCODE_LEN:
            raise ValueError(f'Bad length for code: {code!r}')
        upper_code = code.upper()
        if _UK_RE.match(upper_code):
            self.code = upper_code
        else:
            raise ValueError(f'{code!r} does not match UK postcode pattern')
