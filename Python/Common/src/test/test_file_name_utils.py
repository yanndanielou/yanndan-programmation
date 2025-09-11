# -*-coding:Utf-8 -*

import pytest

from src.common import file_name_utils


file_extension_test_data = [
    ("http://vevtv.top:2103/movie/412910643GRB/dn5QFp3/24950.mp4", ".mp4"),
    ("http://oxtv.top:2103/series/412910643GRB/dn5QFp3/57996.mkv", ".mkv"),
    ("http://vefextv.top:2103/412910643GRB/dn5QFp3/37744", None),
]


class TestFileExtension:

    @pytest.mark.parametrize(
        "full_path, expected_extension",
        file_extension_test_data,
    )
    def test_full_path(self, full_path: str, expected_extension: str) -> None:
        assert file_name_utils.file_extension_from_full_path(full_path) == expected_extension


class TestFileName:

    @pytest.mark.parametrize(
        "full_path, expected_file_name",
        [("Input_for_tests\\main_word.docx", "main_word"), ("Input_for_tests/main_word.docx", "main_word"), (r"Input_for_tests\main_word.docx", "main_word")],
    )
    def test_file_name(self, full_path: str, expected_file_name: str) -> None:
        assert file_name_utils.get_file_name_without_extension_from_full_path(full_path) == expected_file_name
