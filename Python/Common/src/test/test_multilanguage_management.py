# -*-coding:Utf-8 -*

import unittest

from parameterized import parameterized_class

from common import multilanguage_management
from common import unit_tests_helpers


@parameterized_class(("current_language", "expected_translated"), [
   ("fr", "Application de Changement de Langue"),
   ("en", "Language Switcher App")
])
class TestMultilanguage(unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName:str='runTest'):
        super().__init__(methodName)

    def test_default(self)->None:
        multilanguage = multilanguage_management.MultilanguageManagement("src/test/example_translation_file.json",self.current_language)
        self.assertEqual(self.expected_translated, multilanguage.get_current_language_translation("application_title"))

    def test_switch_language(self)->None:
        multilanguage = multilanguage_management.MultilanguageManagement("src/test/example_translation_file.json",self.current_language)
        self.assertEqual(self.expected_translated, multilanguage.get_current_language_translation("application_title"))
        
        multilanguage.switch_to_language("de")
        self.assertEqual("Sprachwechsler-App", multilanguage.get_current_language_translation("application_title"))

        multilanguage.switch_to_language(self.current_language)
        self.assertEqual(self.expected_translated, multilanguage.get_current_language_translation("application_title"))

    def test_non_existing_default_and_current_language_returns_key(self)->None:
        multilanguage = multilanguage_management.MultilanguageManagement("src/test/example_translation_file.json","pz","tts")
        self.assertTrue("application_title" in multilanguage.get_current_language_translation("application_title"))

if __name__ == "__main__":
    unittest.main()
