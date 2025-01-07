# -*-coding:Utf-8 -*

import xspf
import unittest
import Dependencies.Common.unit_tests_helpers


class TestM3uFileParser(Dependencies.Common.unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  
        self.checker:xspf.XspfFileContent = xspf.XspfFileCreator()


    def test_construction(self):
        """ Number of results """
        # Positive test case
        
        self.xspf_file_content = xspf.XspfFileContent(title="Whatsapp", location="C:\\Users\\fr232487\\Downloads\\WhatsApp Video 2024-11-02 at 08.49.46.mp4")
        self.checker.write(self.xspf_file_content, "test.xspf")
        self.assertIsFile("test.xspf")
        
        
    def test_toto(self):
        """ Number of results """
        # Positive test case

        self.assertTrue(False)
        
        
if __name__ == "__main__":
    unittest.main()
    