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
        
    
if __name__ == "__main__":
    unittest.main()
