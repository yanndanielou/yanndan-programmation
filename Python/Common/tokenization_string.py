# -*-coding:Utf-8 -*

#https://www.tutorialspoint.com/5-simple-ways-to-perform-tokenization-in-python

import nltk

nltk.download('punkt')
nltk.download('punkt_tab')

def tokenize_text_with_nltk_word_tokenize(text_to_tokenize:str):
    tokens = nltk.word_tokenize(text_to_tokenize)
    return tokens

def tokenize_text_with_nltk_sent_tokenize(text_to_tokenize:str):
    tokens = nltk.sent_tokenize(text_to_tokenize)
    return tokens
