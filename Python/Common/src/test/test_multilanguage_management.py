# -*-coding:Utf-8 -*

import pytest

from parameterized import parameterized_class

from src.common import multilanguage_management


expected_translations = [
    ("fr", "Application de Changement de Langue"),
    ("en", "Language Switcher App"),
]


class TestMultilanguage:

    @pytest.mark.parametrize(
        "current_language,expected_translated", expected_translations
    )
    def test_default(self, current_language: str, expected_translated: str) -> None:
        multilanguage = multilanguage_management.MultilanguageManagement(
            "src/test/example_translation_file.json", current_language
        )
        assert expected_translated == multilanguage.get_current_language_translation(
            "application_title"
        )

    @pytest.mark.parametrize(
        "current_language,expected_translated", expected_translations
    )
    def test_switch_language(
        self, current_language: str, expected_translated: str
    ) -> None:
        multilanguage = multilanguage_management.MultilanguageManagement(
            "src/test/example_translation_file.json", current_language
        )
        assert expected_translated == multilanguage.get_current_language_translation(
            "application_title"
        )

        multilanguage.switch_to_language("de")
        assert "Sprachwechsler-App" == multilanguage.get_current_language_translation(
            "application_title"
        )

        multilanguage.switch_to_language(current_language)
        assert expected_translated == multilanguage.get_current_language_translation(
            "application_title"
        )

    def test_non_existing_default_and_current_language_returns_key(self) -> None:
        multilanguage = multilanguage_management.MultilanguageManagement(
            "src/test/example_translation_file.json", "pz", "tts"
        )
        assert "application_title" in multilanguage.get_current_language_translation(
            "application_title"
        )
