# -*-coding:Utf-8 -*


import os
import unittest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from closethebox import application
from common import unit_tests_helpers
from logger import logger_config

class TestApplicationWithoutHmi(unit_tests_helpers.TestCaseBase):
    """ TestApplicationWithoutHmi """

    def __init__(self, methodName:str='runTest')->None:
        super().__init__(methodName)  

        self.checker:application.Application = application.Application()


    def test_get_two_dices_all_combinaisons_with_occurences(self)->None:
        """ Number of results """
        two_dices_all_combinaisons_with_occurences:dict[int, int]= self.checker.get_two_dices_all_combinaisons_with_occurences()
        self.assertEqual(two_dices_all_combinaisons_with_occurences[2],1)
        self.assertEqual(two_dices_all_combinaisons_with_occurences[3],2)
        self.assert_length(two_dices_all_combinaisons_with_occurences,11)



 
if __name__ == "__main__":
    unittest.main()
