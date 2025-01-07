# -*-coding:Utf-8 -*

import unittest

import unit_tests_helpers
import file_name_utils



class TestFileExtension(unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  

    def test_full_path(self):
        self.assertEqual(file_name_utils.file_extension_from_full_path("http://vevoxtv.top:2103/movie/412910643GRB/dn5QFp3/24950.mp4"), ".mp4")
        self.assertEqual(file_name_utils.file_extension_from_full_path("http://vevoxtv.top:2103/series/412910643GRB/dn5QFp3/57996.mkv"), ".mkv")
        self.assertIsNone(file_name_utils.file_extension_from_full_path("http://vevoxtv.top:2103/412910643GRB/dn5QFp3/37744"))

    
if __name__ == "__main__":
    unittest.main()
    