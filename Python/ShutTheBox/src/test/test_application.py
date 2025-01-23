# -*-coding:Utf-8 -*

import pytest

import os
import unittest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from closethebox import application
from common import unit_tests_helpers
from logger import logger_config


checker:application.Application = application.Application()

        
class TestOneStep:
    
 def test_last_step(self)->None:
        all_possibilities_with_hatches:list[application.OneGame] = checker.compute_all_possibilities_with_hatches([1,2,3])
        
        assert all_possibilities_with_hatches is not None
        

        
class TestUniqueccombinaisonsToReachExacltySumUsingElementNoMoreThanOnce:
    """ TestApplicationWithoutHmi """

    def test_impossible(self)->None:
        assert not checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1],12)
        assert not checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1,2,3],7)
        assert not checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1,5,7],4)
        
    def test_chatgpt(self)->None:
        liste = [2, 3, 5, 7]
        somme_a_atteindre = 7
        assert checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once(liste,somme_a_atteindre) == [[2, 5], [7]]


    def test_simple(self)->None:
        assert checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1],1) == [[1]]
        assert checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1,2,3],2) == [[2]]

    

class TestApplicationMisc:
    """ TestApplicationWithoutHmi """

    def get_all_unique_combinaisons_to_attains_exaclty_sum_using_element_no_more_than_once(self)->None:
        assert checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1,2,3],2) == set(set(2))
    

    def test_get_two_dices_all_combinaisons_with_occurences(self)->None:
        """ Number of results """
        two_dices_all_combinaisons_with_occurences:dict[int, int]= checker.get_two_dices_all_combinaisons_with_occurences()
        assert two_dices_all_combinaisons_with_occurences[2] == 1
        assert two_dices_all_combinaisons_with_occurences[3] == 2
        assert len(two_dices_all_combinaisons_with_occurences) == 11



 
if __name__ == "__main__":
    unittest.main()
