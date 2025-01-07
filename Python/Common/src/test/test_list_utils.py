# -*-coding:Utf-8 -*

import unittest

import unit_tests_helpers
import list_utils


class TestListEquals(unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  

    def test_list_with_order(self):
        self.assertTrue(list_utils.are_list_equals([0],[0]))
        self.assertTrue(list_utils.are_list_equals([0,1],[0,1]))
        self.assertTrue(list_utils.are_list_equals([0,1],[1,0]))
        
class TestAreAllElementsOfListIncludedInList(unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  

    def test_list_with_order(self):
        self.assertTrue(list_utils.are_all_elements_of_list_included_in_list([0],[0]))
        self.assertTrue(list_utils.are_all_elements_of_list_included_in_list([1, 2],[1, 2, 3, 1, 1, 2, 2]))
        self.assertTrue(list_utils.are_all_elements_of_list_included_in_list(['x', 'y', 'z'],['x', 'a', 'y', 'x', 'b', 'z']))
        self.assertTrue(list_utils.are_all_elements_of_list_included_in_list([0,1],[0,1]))
        self.assertTrue(list_utils.are_all_elements_of_list_included_in_list([0,1,1],[0,1,1,2]))
        self.assertFalse(list_utils.are_all_elements_of_list_included_in_list([0,1,2],[0,1,3]))

if __name__ == "__main__":
    unittest.main()
