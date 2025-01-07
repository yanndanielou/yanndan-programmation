# -*-coding:Utf-8 -*


import os
import unittest

import application
import main_view
import Dependencies.Common.unit_tests_helpers
import Dependencies.Logger.logger_config as logger_config


class TestApplicationWithoutHmi(Dependencies.Common.unit_tests_helpers.TestCaseBase):
    """ TestApplicationWithoutHmi """

    def __init__(self, methodName:str='runTest')->None:
        super().__init__(methodName)  
        self._main_view:main_view.M3uToFreeboxMainView = main_view.M3uToFreeboxMainView()

        self.checker:application.M3uToFreeboxApplication = application.M3uToFreeboxApplication(self._main_view)


    def test_create_all_xspf_light_m3u(self)->None:
        """ Number of results """
        self.__test_create_all_xspf_m3u("output_light", "light.m3u")
        
    def test_create_all_xspf_zfull_m3u(self)->None:
        """ Number of results """                
        self.__test_create_all_xspf_m3u("output_tv_channels_412910643GRB_plus_2024", "tv_channels_412910643GRB_plus_2024-10-08.m3u")

        
    def __test_create_all_xspf_m3u(self, output_directory_name:str, m3u_file_name:str)->None:
        """ Number of results """
        # Positive test case
        
        xspf_output_files_directory = output_directory_name
        
        if not os.path.exists(xspf_output_files_directory):
           os.makedirs(xspf_output_files_directory)
        
        self.checker.load_file(m3u_file_name)
        
        number_files_created = 0
        for m3u_entry in self.checker.m3u_library.m3u_entries:
            number_files_created += 1
            
            logger_config.print_and_log_info_if(number_files_created%100 == 0, f"Number of m3u entry processed:{number_files_created} / {len(self.checker.m3u_library.m3u_entries)}. Progress:{format(100*number_files_created/len(self.checker.m3u_library.m3u_entries),'.2f')}%")
            self.assertTrue(self.checker.create_xspf_file_by_id(xspf_output_files_directory + "/",m3u_entry.id, False))
        
        
        
        
        
if __name__ == "__main__":
    unittest.main()
    