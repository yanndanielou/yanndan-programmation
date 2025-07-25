# -*-coding:Utf-8 -*
"""Utils for strings"""

import math
from typing import Optional

from logger import logger_config

from unidecode import unidecode


def format_filename(input_original_string: str, allow_spaces: bool = True) -> str:
    """Take a string and return a valid filename constructed from the string.
    Uses a whitelist approach: any characters not present in valid_chars are
    removed. Also spaces are replaced with underscores.

    Note: this method may produce invalid filenames such as ``, `.` or `..`
    When I use this method I prepend a date string like '2009_01_15_19_46_32_'
    and append a file extension like '.txt', so I avoid the potential of using
    an invalid filename.

    Taken from https://gist.github.com/seanh/93666#file-formatfilename-py

    """

    windows_reserved_filemanes = [
        "CON, PRN, AUX, NUL, COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9, LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9"
    ]  # pylint: disable=line-too-long
    forbidden_windows_caracters = [
        ("<", "(less than)"),
        (">", "(greater than)"),
        (":", "(colon - sometimes works, but is actually NTFS Alternate Data Streams)"),
        ('"', "(double quote)"),
        ("/", "(forward slash)"),
        ("\\", "(backslash)"),
        ("|", "(vertical bar or pipe)"),
        ("?", "(question mark)"),
        ("*", "(asterisk)"),
    ]  # pylint: disable=line-too-long

    not_convenient_caracters = [chr(9600), chr(9604)]

    # 0-31 (ASCII control characters)
    windows_non_printable_characters = list(
        map(chr, range(0, 31))
    )  # previously list(map(lambda x: chr(x), range(0, 31)))

    if input_original_string in windows_reserved_filemanes:
        return "_" + input_original_string

    for forbidden_windows_caracter in (
        list(map(lambda x: x[0], forbidden_windows_caracters))
        + windows_non_printable_characters
        + not_convenient_caracters
    ):  # pylint: disable=line-too-long
        input_original_string = input_original_string.replace(
            forbidden_windows_caracter, ""
        )

    if not allow_spaces:
        input_original_string = input_original_string.replace(" ", "_")

    return input_original_string


def right_part_after_last_occurence(input_string: str, separator: str) -> str:
    """return the right_part_after_last_occurence: usefull to get file extensions for instance"""

    splitted_tab = input_string.split(separator)
    return splitted_tab[len(splitted_tab) - 1]


def without_diacritics(input_string: str) -> str:
    """return string without diacritics (accents, etc)"""
    return unidecode(input_string)


def text_to_valid_enum_value_text(raw_text: str) -> Optional[str]:
    if type(raw_text) is not str and math.isnan(raw_text):
        logger_config.print_and_log_error(
            f"text_to_valid_enum_value_text: Could not treat {raw_text}"
        )
        return None

    return (
        raw_text.replace("/", "_")
        .replace(", ", "_")
        .replace(" ", "_")
        .replace("-", "_")
        .replace(",", "_")
        .upper()
    )
