# -*-coding:Utf-8 -*

#https://www.tutorialspoint.com/5-simple-ways-to-perform-tokenization-in-python

import nltk
import shlex
import re

nltk.download('punkt')
nltk.download('punkt_tab')


def tokenize_text_with_nltk_regexp_tokenizer(text_to_tokenize:str):
    toknizer = RegexpTokenizer(r'''\w'|\w+|[^\w\s]''')
    tokens = toknizer.tokenize(text_to_tokenize)
    return tokens


from nltk import RegexpTokenizer


def tokenize_text_with_nltk_word_tokenize(text_to_tokenize:str, language="english"):
    tokens = nltk.word_tokenize(text_to_tokenize, language)
    return tokens

def tokenize_text_with_nltk_sent_tokenize(text_to_tokenize:str, language="english"):
    tokens = nltk.sent_tokenize(text_to_tokenize, language)
    return tokens

def tokenize_text_with_shlex_split(text_to_tokenize:str):
    tokens = shlex.split(text_to_tokenize)
    return tokens


def tokenize_text_with_str_split(text_to_tokenize:str):
    tokens = text_to_tokenize.split([" ", ",", "!"])
    return tokens

def tokenize_text_with_re_split(text_to_tokenize:str):
    tokens = re.split(r'\'[;,\s]+', text_to_tokenize)
    return tokens
