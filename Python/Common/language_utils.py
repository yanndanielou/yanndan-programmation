# -*-coding:Utf-8 -*

from py3langid.langid import LanguageIdentifier, MODEL_FILE 
from langdetect import detect_langs

def detect_language_with_langid(line): 
    identifier = LanguageIdentifier.from_pickled_model(MODEL_FILE, norm_probs=True) 
    lang, prob = identifier.classify(line)
    return lang, prob

def detect_language_with_langdetect(line): 
    try: 
        langs = detect_langs(line) 
        for item in langs: 
            # The first one returned is usually the one that has the highest probability
            return item.lang, item.prob 
    except: return "err", 0.0 

def get_full_language_name(short_language_name):
    if short_language_name[0] == "fr":
        return "French"
    return "English"
