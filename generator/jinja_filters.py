import re

def first_date_filter(value: str) -> str:
    if not isinstance(value, str):
        raise Exception(f"Value error: {value}")

    match = re.search(r'\b(\d{4})\b', value)

    if match:
        return match.group(1)

    raise Exception(f"Date filtering error: {value}")

