# -*-coding:Utf-8 -*

import m3u
import unittest
import Dependencies.Common.unit_tests_helpers


class TestM3uFileParser(Dependencies.Common.unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  

        # Test data 
        self.a1 = 20
        self.a2 = 'Ram'
        self.b1 = 10
        self.b2 = 0
        self.checker = m3u.M3uFileParser()  # Creating the object

    def test_number_of_results(self):
        """ Number of results """
        # Positive test case
        result:list[m3u.M3uEntry] = self.checker.parse_file("tv_channels_412910643GRB_plus_2024-10-08.m3u")
        self.assertNotEmpty(result)

        self.assertEqual(len(result), 100914)
                
                
    def test_first_entry(self):
        # Positive test case
        result:list[m3u.M3uEntry] = self.checker.parse_file("tv_channels_412910643GRB_plus_2024-10-08.m3u")
        self.assertNotEmpty(len(result))
        
        first_m3u_entry:m3u.M3uEntry = result[0]
        
        self.assertNotEmpty(first_m3u_entry.tvg_id)
        self.assertEqual(first_m3u_entry.tvg_id, "TF1.fr")

        self.assertEqual(first_m3u_entry.tvg_name, "|FR| TF1 SD")
        self.assertEqual(first_m3u_entry.tvg_logo, "https://i.imgur.com/LMxTAzY.png")
        self.assertEqual(first_m3u_entry.group_title, "FR TV SD (FRANCE)")
        self.assertEqual(first_m3u_entry.original_raw_title, "|FR| TF1 SD")
        
        self.assertEqual(first_m3u_entry.link, "http://vevoxtv.top:80/412910643GRB/dn5QFp3/12071")

        
        


        # Negative test case for data type


if __name__ == "__main__":
    unittest.main()
    