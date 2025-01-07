# -*-coding:Utf-8 -*

import os
import unittest

import unit_tests_helpers
import string_utils

class WithoutDiacritics(unit_tests_helpers.TestCaseBase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)

    def test_remove_french_accents(self):
        self.assertEqual('ete', string_utils.without_diacritics('été'))
        self.assertEqual('Francois', string_utils.without_diacritics('François'))

    def test_remove_slovene_accents(self):
        self.assertEqual('kozuscek', string_utils.without_diacritics('kožušček'))


class Separators(unit_tests_helpers.TestCaseBase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)


    def test_right_part_after_last_occurence(self):
        self.assertEqual(string_utils.right_part_after_last_occurence("abcde" , "d"), "e")

class TestApplicationWithoutHmi(unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  


    def __assert_format_filename_returns_entry(self, text_to_test):
        with self.subTest():
            self.assertEqual(string_utils.format_filename(text_to_test), text_to_test)

    def windows_reserved_cararcters(self):
        """ """
        #windows_reserved_filemanes = ["CON, PRN, AUX, NUL, COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9, LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9"]
        pass
        
    def test_forbidden_printable_ascii_characters_windows(self):
        """https://stackoverflow.com/questions/1976007/what-characters-are-forbidden-in-windows-and-linux-directory-names"""
        forbidden_windows_caracters = [("<","(less than)"), (">" ,"(greater than)"), (":", "(colon - sometimes works, but is actually NTFS Alternate Data Streams)"),('"',"(double quote)"),("/","(forward slash)"),("\\","(backslash)"),("|","(vertical bar or pipe)"),("?","(question mark)"),("*","(asterisk)")]

        for forbidden_caracter in forbidden_windows_caracters:
            self.assertEqual(string_utils.format_filename("a" + forbidden_caracter[0]), "a")

    def test_transform_file_name(self):
        """ test_transform_file_name """
        
        self.__assert_format_filename_returns_entry("a")
        
        self.__assert_format_filename_returns_entry("à.txt")
        self.__assert_format_filename_returns_entry("â.txt")
        self.__assert_format_filename_returns_entry("ä.txt")
        self.__assert_format_filename_returns_entry("è.txt")
        self.__assert_format_filename_returns_entry("é.txt")
        self.__assert_format_filename_returns_entry("e.txt")
        self.__assert_format_filename_returns_entry("ç.txt")
        self.__assert_format_filename_returns_entry("c.txt")
        self.__assert_format_filename_returns_entry("@.txt")
        self.__assert_format_filename_returns_entry("+.txt")
        self.__assert_format_filename_returns_entry("'.txt")
        self.__assert_format_filename_returns_entry("ô.txt")
        self.__assert_format_filename_returns_entry("ö.txt")
        self.__assert_format_filename_returns_entry("û.txt")
        self.__assert_format_filename_returns_entry("ü.txt")
        self.__assert_format_filename_returns_entry("ï.txt")
        self.__assert_format_filename_returns_entry("î.txt")
        self.__assert_format_filename_returns_entry("ââäâaaàèéêë.txt")

    
if __name__ == "__main__":
    unittest.main()
    