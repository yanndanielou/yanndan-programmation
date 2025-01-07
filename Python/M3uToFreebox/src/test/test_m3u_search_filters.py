# -*-coding:Utf-8 -*

import m3u
import unittest
import Dependencies.Common.unit_tests_helpers
from m3u_search_filters import TitleContainsAllWordsFilter


class TestM3uSearchFilter(Dependencies.Common.unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)

    def test_TitleContainsAllWordsFilter_whole_word_case_sensitive(self):
        
        #

        m3u_entry_string_definition = m3u.M3uEntryStringDefinition()
        m3u_entry_string_definition.line1 = """#EXTINF:-1 tvg-id="" tvg-name="Maman, j'ai raté l'avion ! (True FR) FHD 1990" tvg-logo="https://image.tmdb.org/t/p/w600_and_h900_bestv2/aP9UrDpKS5i5PCiYKDgJvkRz7ne.jpg" group-title="FILMS DE FIN D’ANNÉE",Maman, j'ai raté l'avion ! (True FR) FHD 1990"""
        m3u_entry_string_definition.line2 = "http://toto.top:2103/movie/412910643GRB/dn5QFp3/26566.mp4"

        maman_jai_rate_lavion_m3u_entry = m3u.M3uEntry(m3u_entry_string_definition)


        self.contains_all_worlds_case_sensitive = TitleContainsAllWordsFilter(False, True, "TitleContainsAllWordsFilter_whole_word_case_sensitive")
        #self.assertTrue(self.contains_all_worlds_case_sensitive.match_m3u(maman_jai_rate_lavion_m3u_entry, "Maman l'avion"))
        self.assertTrue(self.contains_all_worlds_case_sensitive.match_m3u(maman_jai_rate_lavion_m3u_entry, "Maman avion"))
        self.assertTrue(self.contains_all_worlds_case_sensitive.match_m3u(maman_jai_rate_lavion_m3u_entry, "Mama avio"))

        self.assertFalse(self.contains_all_worlds_case_sensitive.match_m3u(maman_jai_rate_lavion_m3u_entry, "maman avion"))
        self.assertFalse(self.contains_all_worlds_case_sensitive.match_m3u(maman_jai_rate_lavion_m3u_entry, "mama avio"))

        self.contains_all_worlds_whole_word_case_sensitive = TitleContainsAllWordsFilter(True, True, "TitleContainsAllWordsFilter_whole_word_case_sensitive")
        self.assertTrue(self.contains_all_worlds_whole_word_case_sensitive.match_m3u(maman_jai_rate_lavion_m3u_entry, "Maman avion"))
        self.assertFalse(self.contains_all_worlds_whole_word_case_sensitive.match_m3u(maman_jai_rate_lavion_m3u_entry, "maman avion"))

        



        # Negative test case for data type


if __name__ == "__main__":
    unittest.main()
    