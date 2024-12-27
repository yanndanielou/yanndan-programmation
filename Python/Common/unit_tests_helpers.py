import unittest
import pathlib as pl

class TestCaseBase(unittest.TestCase):
    def assertIsFile(self, path):
        if not pl.Path(path).resolve().is_file():
            raise AssertionError("File does not exist: %s" % str(path))
            
    def assertEmpty(self, obj):
        self.assertFalse(obj)

    def assertNotEmpty(self, obj):
        self.assertTrue(obj)
            
    def assertListContains(self,obj:list, element):
        self.assertTrue(element in obj)
        
    def assertListDoesNotContains(self,obj:list, element):
        self.assertFalse(element in obj)

