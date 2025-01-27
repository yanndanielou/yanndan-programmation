# -*-coding:Utf-8 -*

import pytest

from common import file_name_utils


class TestFileExtension():

    def test_full_path(self) -> None:
        assert file_name_utils.file_extension_from_full_path("http://vevoxtv.top:2103/movie/412910643GRB/dn5QFp3/24950.mp4") == ".mp4"
        assert file_name_utils.file_extension_from_full_path("http://vevoxtv.top:2103/series/412910643GRB/dn5QFp3/57996.mkv") == ".mkv"
        assert file_name_utils.file_extension_from_full_path("http://vevoxtv.top:2103/412910643GRB/dn5QFp3/37744" is not None
