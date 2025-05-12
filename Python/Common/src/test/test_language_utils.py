# -*-coding:Utf-8 -*

import pytest

from src.common import language_utils

class TestFileExtension():

    def test_full_path(self) -> None:

        assert "French" == language_utils.get_full_language_name(language_utils.detect_language_with_langid("Maman, j'ai raté l'avion ! (True FR) FHD 1990"))
        assert "French" == language_utils.get_full_language_name(language_utils.detect_language_with_langdetect("Maman, j'ai raté l'avion ! (True FR) FHD 1990"))
