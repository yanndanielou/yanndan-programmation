# -*-coding:Utf-8 -*
""" Module useful for multilanguage gui """
import json


class MultilanguageManagement():
    """ useful class for multilanguage gui """

    def __init__(self, translations_json_file_path:str, default_language:str):
        # Langue par défaut (français) pour les traductions manquantes
        self._default_language = default_language

        self._load_translations(translations_json_file_path)

    def _load_translations(self, file_path:str)->None:
        """ Charger les traductions depuis le fichier JSON """
        with open(file_path, 'r', encoding='utf-8') as file:
            self._translations = json.load(file)


    # Fonction pour récupérer la traduction ou utiliser la langue par défaut
    def get_translation(self, lang, key, translations):
        """ return translation """
        # Si la traduction n'est pas disponible dans la langue choisie, utiliser la langue par défaut
        return translations.get(lang, {}).get(key, translations.get(self._default_language, {}).get(key, ""))
