import pandas
from typing import Optional


def string_optional_element(row: pandas.Series, column_name: str) -> Optional[str]:
    raw_value = row[column_name]
    if isinstance(raw_value, str):
        return raw_value
    else:
        return None


def is_string_element_at_value(row: pandas.Series, column_name: str, tested_value: str) -> bool:
    raw_value = row[column_name]
    if isinstance(raw_value, str):
        return str(raw_value) == tested_value
    return False


def string_element(row: pandas.Series, column_name: str) -> str:
    raw_value = str(row[column_name])
    assert isinstance(raw_value, str)
    return raw_value
