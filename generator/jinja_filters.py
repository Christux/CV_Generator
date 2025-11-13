import re

def first_date_filter(value: str) -> str:
    """Extract the first 4-digit year from a string.

    This function searches for the first occurrence of a 4-digit sequence
    (representing a year) in the given string. If found, it returns the year
    as a string. Otherwise, it raises an exception.

    Args:
        value (str): The input string to search within.

    Returns:
        str: The first 4-digit year found in the input string.

    Raises:
        Exception: If the input is not a string.
        Exception: If no 4-digit year is found in the string.
    """
    if not isinstance(value, str):
        raise Exception(f"Value error: {value}")

    match = re.search(r'\b(\d{4})\b', value)

    if match:
        return match.group(1)

    raise Exception(f"Date filtering error: {value}")
