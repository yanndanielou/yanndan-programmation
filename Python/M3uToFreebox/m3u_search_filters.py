""" Filters to search M3u entry by criteria """
# -*-coding:Utf-8 -*

from abc import ABC
from abc import abstractmethod

import importlib

from Dependencies.Common.singleton import Singleton

import Dependencies.Common.tokenization_string as tokenization_string

import Dependencies.Common.language_utils as language_utils

import Dependencies.Common.list_utils as list_utils

from m3u import M3uEntry

import re

class M3uEntryFilter:
    """ base class """
    def __init__(self, label:str):
        self._label:str = label

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value


class M3uFiltersManager(metaclass=Singleton):
    """ Manager of m3u filters"""
    def __init__(self):# type: ignore
        self._by_title_filters : list[M3uEntryByTitleFilter] = []
        self._by_title_filters.append(TitleContainsExactlyFilter(True, "Contains Exactly (case sensitive)"))
        self._by_title_filters.append(TitleContainsExactlyFilter(False, "Contains Exactly (case NOT sensitive)")) 
        self._by_title_filters.append(TitleContainsAllWordsFilter(False, True, "Contains all words (case sensitive)"))
        self._by_title_filters.append(TitleContainsAllWordsFilter(False, False, "Contains all words (case NOT sensitive)")) 
        self._by_title_filters.append(TitleContainsAllWordsFilter(True, True, "Contains all words (whole worlds case sensitive)"))
        self._by_title_filters.append(TitleContainsAllWordsFilter(True, False, "Contains all words (whole worlds case NOT sensitive)"))
        self._by_title_filters.append(TitleMatchesFilterTextRegex(True, "Matches Regex"))
        self._by_title_filters.append(TitleMatchesFilterTextRegex(False, "Matches Regex (not case sensitive: treat texts as lower)")) 

        self._by_type_filters : list[M3uEntryByTypeFilter] = []
        self._by_type_filters.append(M3uEntryByTypeFilter(None))
        for e in M3uEntry.EntryType:
            self._by_type_filters.append(M3uEntryByTypeFilter(e))
        

    @property
    def by_title_filters(self):
        """ Getter filters """
        return self._by_title_filters

    @by_title_filters.setter
    def by_title_filters(self, value):
        self._by_title_filters = value

        
    @property
    def by_type_filters(self):
        """ Getter filters """
        return self._by_type_filters

    @by_type_filters.setter
    def by_type_filters(self, value):
        self._by_type_filters = value


class M3uEntryByTypeFilter(M3uEntryFilter):
    def __init__(self, entry_type:M3uEntry.EntryType):
        super().__init__("Any" if entry_type is None else str(entry_type.value))
        self._entry_type:M3uEntry.EntryType = entry_type

    def match_m3u(self, m3u_entry:M3uEntry)->bool:
        if self._entry_type is None:
            return True
        return self._entry_type == m3u_entry.type
    

class M3uEntryByTitleFilter(M3uEntryFilter):
    """ base class """
    def __init__(self, case_sensitive:bool, label:str):
        super().__init__(label)
        self._case_sensitive:bool = case_sensitive
    
    @property
    def case_sensitive(self)->bool:
        """ case_sensitive getter """
        return self._case_sensitive

    @case_sensitive.setter
    def case_sensitive(self, value:bool)->None:
        self._case_sensitive = value

      
    @abstractmethod
    def match_m3u(self, m3u_entry:M3uEntry, filter_text:str) -> bool:
        """ Check if match m3u """
        raise NotImplementedError()


class TitleContainsExactlyFilter(M3uEntryByTitleFilter):
    """ TitleContainsExactlyFilter """
    def __init__(self, case_sensitive:bool, label:str):
        super().__init__(case_sensitive, label)

    def match_m3u(self, m3u_entry:M3uEntry, filter_text:str)->bool:
        if self._case_sensitive:
            return filter_text in m3u_entry.original_raw_title
        return filter_text.lower() in m3u_entry.original_raw_title.lower()

class TitleMatchesFilterTextRegex(M3uEntryByTitleFilter):
    """ TitleMatchesFilterTextRegex """
    def __init__(self, case_sensitive, label):
        super().__init__(case_sensitive, label)
        
        self._filter_text = None
        self._regex_pattern = None

    
    def match_m3u(self, m3u_entry:M3uEntry, filter_text):

        if not self._case_sensitive:
            filter_text = filter_text.lower()

        if self._filter_text != filter_text:
            self._filter_text = filter_text
            self._regex_pattern = re.compile(filter_text)


        m3u_entry_original_raw_title = m3u_entry.original_raw_title if self.case_sensitive else m3u_entry.original_raw_title.lower()

        match = self._regex_pattern.match(m3u_entry_original_raw_title)
        return match is not None

class TitleContainsAllWordsFilter(M3uEntryByTitleFilter):
    """ TitleContainsExactlyFilter """
    def __init__(self, whole_words:bool, case_sensitive:bool, label:str):
        super().__init__(case_sensitive, label)
        self._whole_words = whole_words

        self._filter_text = None
        self._filter_text_language = None
        self._filter_text_words = None
    
    def recompute_filter_text_words_and_language(self, filter_text:str):
        if self._filter_text != filter_text:
            self._filter_text = filter_text
            self._filter_text_language = language_utils.get_full_language_name(language_utils.detect_language_with_langid(filter_text))
            self._filter_text_words = tokenization_string.tokenize_text_with_nltk_regexp_tokenizer(filter_text)


    def match_m3u(self, m3u_entry:M3uEntry, filter_text:str):
        
        if not self._whole_words:
            filter_text_words = tokenization_string.tokenize_text_with_nltk_regexp_tokenizer(filter_text)
            for filter_word in filter_text_words:
                title_contains_exactly_word = TitleContainsExactlyFilter(self.case_sensitive, self.label + filter_word)
                if not title_contains_exactly_word.match_m3u(m3u_entry, filter_word):
                    return False
                
            return True

        else:
            m3u_entry_original_raw_title = m3u_entry.original_raw_title if self.case_sensitive else m3u_entry.original_raw_title.lower()
            if not self.case_sensitive:
                filter_text = filter_text.lower()

            self.recompute_filter_text_words_and_language(filter_text)

            self._m3u_entry_original_words = tokenization_string.tokenize_text_with_nltk_regexp_tokenizer(m3u_entry_original_raw_title)

            return list_utils.are_all_elements_of_list_included_in_list(self._filter_text_words, self._m3u_entry_original_words)

if __name__ == "__main__":
    # sys.argv[1:]
    main = importlib.import_module("main")
    main.main()

