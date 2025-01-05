""" Helpers for unit tests """

import unittest
import pathlib

class TestCaseBase(unittest.TestCase):
    """ Base class of test cases """
    def assert_is_file(self, path_str:str)->None:
        """ Assert file exists """
        if not pathlib.Path(path_str).resolve().is_file():
            raise AssertionError(f"File does not exist: {str(path_str)}")

    def assert_empty(self, obj)->None:
        """ Assert list is empty """
        self.assertFalse(obj)

    def assert_not_empty(self, obj)->None:
        """ Assert list is not empty """
        self.assertTrue(obj)

    def assert_list_contains(self,obj:list, element)->None:
        """ Assert list contains element """
        self.assertTrue(element in obj)

    def assert_list_does_not_contain(self,obj:list, element)->None:
        """ Assert list does not contain element """
        self.assertFalse(element in obj)

