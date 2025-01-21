# -*-coding:Utf-8 -*


import os
import unittest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from closethebox import application
from common import unit_tests_helpers
from logger import logger_config

class TestUniqueccombinaisonsToReachExacltySumUsingElementNoMoreThanOnce(unit_tests_helpers.TestCaseBase):
    """ TestApplicationWithoutHmi """

    def __init__(self, methodName:str='runTest')->None:
        super().__init__(methodName)  

        self.checker:application.Application = application.Application()

    def test_impossible(self)->None:
        self.assert_empty(self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1],12))

    def test_simple(self)->None:
        self.assertEqual(self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1],1),set(set([1])))

        self.assertEqual(self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1,2,3],2),set(set([2])))
    

class TestApplicationMisc(unit_tests_helpers.TestCaseBase):
    """ TestApplicationWithoutHmi """

    def __init__(self, methodName:str='runTest')->None:
        super().__init__(methodName)  

        self.checker:application.Application = application.Application()

    def get_all_unique_combinaisons_to_attains_exaclty_sum_using_element_no_more_than_once(self)->None:
        self.assertEqual(self.checker.get_all_unique_combinaisons_to_attains_exaclty_sum_using_element_no_more_than_once([1,2,3],2),set(set(2)))
    

    def test_get_two_dices_all_combinaisons_with_occurences(self)->None:
        """ Number of results """
        two_dices_all_combinaisons_with_occurences:dict[int, int]= self.checker.get_two_dices_all_combinaisons_with_occurences()
        self.assertEqual(two_dices_all_combinaisons_with_occurences[2],1)
        self.assertEqual(two_dices_all_combinaisons_with_occurences[3],2)
        self.assert_length(two_dices_all_combinaisons_with_occurences,11)



 
if __name__ == "__main__":
    unittest.main()
