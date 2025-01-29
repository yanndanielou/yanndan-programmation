# -*-coding:Utf-8 -*
""" Module useful for multilanguage gui """
import json

from typing import List
from logger import logger_config


class MultilanguageManagement:
    """useful class for multilanguage gui"""

    def __init__(
        self,
        translations_json_file_path: str,
        default_language: str,
        current_language: str = "",
    ):
        # Langue par défaut (français) pour les traductions manquantes
        self._default_language = default_language
        self._current_language = (
            current_language if current_language != "" else default_language
        )

        self._load_translations(translations_json_file_path)

    def _load_translations(self, file_path: str) -> None:
        """Charger les traductions depuis le fichier JSON"""
        with open(file_path, "r", encoding="utf-8") as file:
            self._translations = json.load(file)
            logger_config.print_and_log_info(
                f"Translation file {file_path} loaded. Number of translations:{len(self._translations)}"
            )

    # Fonction pour récupérer la traduction ou utiliser la langue par défaut
    def get_translation(self, lang: str, key: str) -> str:
        """return translation"""
        # Si la traduction n'est pas disponible dans la langue choisie, utiliser la langue par défaut
        # return str(self._translations.get(lang, {}).get(key, self._translations.get(self._default_language, {}).get(key, "")))
        translation_key_found = self._translations.get(key, {})

        if translation_key_found is None:
            logger_config.print_and_log_error(
                f"Could not find translation key {key}. Returns it"
            )
            return key

        translation_for_required_language = translation_key_found.get(lang)

        if translation_for_required_language is not None:
            return translation_for_required_language
        else:
            logger_config.print_and_log_info(
                f"No translation in language {lang} found for key {key}. Other languages found:{translation_key_found.keys()}"
            )
            translation_for_default_language = translation_key_found.get(
                self._default_language
            )
            if translation_for_default_language is not None:
                logger_config.print_and_log_info(
                    f"Return default language {self._default_language} translation for key {key}"
                )
                return translation_for_default_language

            else:
                logger_config.print_and_log_warning(
                    f"Return first found language {self._default_language} translation for key {key}, because neither requested lang {lang} nor {self._default_language} translations were found"
                )
                return key + lang
                # return next(iter(translation_key_found.values()))

    def get_current_language_translation(self, key: str) -> str:
        """return translation"""
        return self.get_translation(self._current_language, key)

    def get_available_languages(self) -> List[str]:
        # Default to English if no translations are loaded
        # Get the languages from the first key (assuming all keys have the same languages)
        first_key = next(iter(self._translations))
        return list(self._translations[first_key].keys())

    @property
    def current_language(self) -> str:
        return self._current_language

    def switch_to_language(self, new_language: str) -> None:
        self._current_language = new_language
