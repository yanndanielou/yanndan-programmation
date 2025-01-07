# -*-coding:Utf-8 -*

import unittest

import tokenization_string
import unit_tests_helpers
import file_name_utils



class TestTokenizationString(unit_tests_helpers.TestCaseBase):

    def __init__(self, methodName='runTest'):  
        super().__init__(methodName)  

    def test_two_sentences(self):
        to_test = "This is an example sentence for tokenization. And this is another sentence"
        result_sent_tokenize = tokenization_string.tokenize_text_with_nltk_sent_tokenize(to_test)
        result_word_tokenize = tokenization_string.tokenize_text_with_nltk_word_tokenize(to_test)
        pause = 1
        self.assert_not_empty(result_sent_tokenize)
        self.assert_not_empty(result_word_tokenize)
    
    def test_tokenize_text_with_shlex_split(self):
        maman_jai_rate_lavion_tokens = tokenization_string.tokenize_text_with_nltk_regexp_tokenizer("Maman, j'ai raté l'avion !")
        self.assert_not_empty(maman_jai_rate_lavion_tokens)
        self.assert_list_contains(maman_jai_rate_lavion_tokens,"avion")
        self.assert_list_does_not_contain(maman_jai_rate_lavion_tokens,"l'avion")


if __name__ == "__main__":
    unittest.main()
    