# -*-coding:Utf-8 -*

import unittest

import tokenization_string
import unit_tests_helpers
import file_name_utils



class TestTokenizationString(unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  

    def text_two_sentences(self):
        to_test = "This is an example sentence for tokenization. And this is another sentence"
        result_sent_tokenize = tokenization_string.tokenize_text_with_nltk_sent_tokenize(to_test)
        result_word_tokenize = tokenization_string.tokenize_text_with_nltk_word_tokenize(to_test)
        pause = 1

if __name__ == "__main__":
    unittest.main()
    