# -*-coding:Utf-8 -*

import pytest


from common import tokenization_string, file_name_utils

class TestTokenizationString():

    def test_two_sentences(self) -> None:
        to_test = "This is an example sentence for tokenization. And this is another sentence"
        result_sent_tokenize = tokenization_string.tokenize_text_with_nltk_sent_tokenize(to_test)
        result_word_tokenize = tokenization_string.tokenize_text_with_nltk_word_tokenize(to_test)
        pause = 1
        assert result_sent_tokenize
        assert result_word_tokenize
    
    def test_tokenize_text_with_shlex_split(self) -> None:
        maman_jai_rate_lavion_tokens = tokenization_string.tokenize_text_with_nltk_regexp_tokenizer("Maman, j'ai raté l'avion !")
        assert maman_jai_rate_lavion_tokens
        assert "avion" in maman_jai_rate_lavion_tokens
        assert not "l'avion" in maman_jai_rate_lavion_tokens
