"""
City-level data for SWE project
"""


def create(name: str):
    if not isinstance(name, str):
        raise ValueError(f'Incorrect type for {type(name)=}')
