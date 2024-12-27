""" Filters to search M3u entry by criteria """
# -*-coding:Utf-8 -*

from abc import ABC
from abc import abstractmethod


import Dependencies.Common.string_utils as string_utils
import Dependencies.Logger.logger_config as logger_config

from Dependencies.Common.singleton import Singleton

from m3u import M3uEntry


class M3uFiltersManager(metaclass=Singleton):
    """ Manager of m3u filters"""
    def __init__(self):
        self._by_title_filters : list[M3uEntryByTitleFilter] = []
        self._by_title_filters.append(TitleContainsExactlyFilter(True, "Contains Exactly (case sensitive)"))
        self._by_title_filters.append(TitleContainsExactlyFilter(False, "Contains Exactly (case NOT sensitive)")) 

    @property
    def filters(self):
        """ Getter filters """
        return self._by_title_filters

    @filters.setter
    def filters(self, value):
        self._by_title_filters = value


class M3uEntryByTitleFilter:
    """ base class """
    def __init__(self, case_sensitive:bool, label:str):
        self._case_sensitive:bool = case_sensitive
        self._label:str = label

    @property
    def case_sensitive(self):
        return self._case_sensitive

    @case_sensitive.setter
    def case_sensitive(self, value):
        self._case_sensitive = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

      
    @abstractmethod
    def match_m3u(self, m3u_entry:M3uEntry, filter_text:str) -> bool:
        """ Check if match m3u """
        raise NotImplementedError()


class TitleContainsExactlyFilter(M3uEntryByTitleFilter):
    """ TitleContainsExactlyFilter """
    def __init__(self, case_sensitive, label):
        super().__init__(case_sensitive, label)
        pass
    
    def match_m3u(self, m3u_entry, filter_text):
        if self._case_sensitive:
            return filter_text in m3u_entry.original_raw_title
        return filter_text.lower() in m3u_entry.original_raw_title.lower()
        

    
