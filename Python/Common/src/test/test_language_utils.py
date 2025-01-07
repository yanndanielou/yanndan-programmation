# -*-coding:Utf-8 -*

import unittest

import unit_tests_helpers
import language_utils



class TestFileExtension(unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  

    def test_full_path(self):

        self.assertEqual("French", language_utils.get_full_language_name(language_utils.detect_language_with_langid("Maman, j'ai raté l'avion ! (True FR) FHD 1990")))
        self.assertEqual("French", language_utils.get_full_language_name(language_utils.detect_language_with_langdetect("Maman, j'ai raté l'avion ! (True FR) FHD 1990")))

if __name__ == "__main__":
    unittest.main()
    