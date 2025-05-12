# -*-coding:Utf-8 -*

import pytest
import os

from src.common import string_utils
from enum import auto, Enum


class TestWithoutDiacritics:

    def test_remove_french_accents(self) -> None:
        assert "ete" == string_utils.without_diacritics("été")
        assert "Francois" == string_utils.without_diacritics("François")

    def test_remove_slovene_accents(self) -> None:
        assert "kozuscek" == string_utils.without_diacritics("kožušček")


class TestSeparators:
    def test_right_part_after_last_occurence(self) -> None:
        assert string_utils.right_part_after_last_occurence("abcde", "d") == "e"


class TestApplicationWithoutHmi:

    def __assert_format_filename_returns_entry(self, text_to_test: str) -> None:
        assert string_utils.format_filename(text_to_test) == text_to_test

    def windows_reserved_cararcters(self) -> None:
        """ """
        # windows_reserved_filemanes = ["CON, PRN, AUX, NUL, COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9, LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9"]
        pass

    def test_forbidden_printable_ascii_characters_windows(self) -> None:
        """https://stackoverflow.com/questions/1976007/what-characters-are-forbidden-in-windows-and-linux-directory-names"""
        forbidden_windows_caracters = [
            ("<", "(less than)"),
            (">", "(greater than)"),
            (
                ":",
                "(colon - sometimes works, but is actually NTFS Alternate Data Streams)",
            ),
            ('"', "(double quote)"),
            ("/", "(forward slash)"),
            ("\\", "(backslash)"),
            ("|", "(vertical bar or pipe)"),
            ("?", "(question mark)"),
            ("*", "(asterisk)"),
        ]

        for forbidden_caracter in forbidden_windows_caracters:
            assert string_utils.format_filename("a" + forbidden_caracter[0]) == "a"

    def test_transform_file_name(self) -> None:
        """test_transform_file_name"""

        self.__assert_format_filename_returns_entry("a")

        self.__assert_format_filename_returns_entry("à.txt")
        self.__assert_format_filename_returns_entry("â.txt")
        self.__assert_format_filename_returns_entry("ä.txt")
        self.__assert_format_filename_returns_entry("è.txt")
        self.__assert_format_filename_returns_entry("é.txt")
        self.__assert_format_filename_returns_entry("e.txt")
        self.__assert_format_filename_returns_entry("ç.txt")
        self.__assert_format_filename_returns_entry("c.txt")
        self.__assert_format_filename_returns_entry("@.txt")
        self.__assert_format_filename_returns_entry("+.txt")
        self.__assert_format_filename_returns_entry("'.txt")
        self.__assert_format_filename_returns_entry("ô.txt")
        self.__assert_format_filename_returns_entry("ö.txt")
        self.__assert_format_filename_returns_entry("û.txt")
        self.__assert_format_filename_returns_entry("ü.txt")
        self.__assert_format_filename_returns_entry("ï.txt")
        self.__assert_format_filename_returns_entry("î.txt")
        self.__assert_format_filename_returns_entry("ââäâaaàèéêë.txt")


class TestTextToValidEnumValueText:
    class EnumClassForTests(Enum):
        NONE = auto()
        NO_FIX_CHANGE = auto()
        DUPLICATE = auto()
        NOT_A_BUG = auto()
        NOT_PART_OF_CONTRACT = auto()

    # fmt: off
    text_to_valid_enum_value_text = ["no fix change",
    "not/A/bug",
    "not-A-bug",]
    # fmt: on

    @pytest.mark.parametrize("raw_text", text_to_valid_enum_value_text)
    def test_some_values(self, raw_text: str) -> None:
        assert TestTextToValidEnumValueText.EnumClassForTests[
            string_utils.text_to_valid_enum_value_text(raw_text)
        ]
