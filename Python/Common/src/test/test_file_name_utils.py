# -*-coding:Utf-8 -*

import pytest

from src.common import file_name_utils


file_extension_test_data = [
    ("http://vevoxtv.top:2103/movie/412910643GRB/dn5QFp3/24950.mp4", ".mp4"),
    ("http://vevoxtv.top:2103/series/412910643GRB/dn5QFp3/57996.mkv", ".mkv"),
    ("http://vevoxtv.top:2103/412910643GRB/dn5QFp3/37744", None),
]


class TestFileExtension:

    @pytest.mark.parametrize(
        "full_path, expected_extension",
        file_extension_test_data,
    )
    def test_full_path(self, full_path: str, expected_extension: str) -> None:
        assert (
            file_name_utils.file_extension_from_full_path(full_path)
            == expected_extension
        )
