""" Filters to search M3u entry by criteria """
# -*-coding:Utf-8 -*

from abc import ABC
from abc import abstractmethod


import Dependencies.Common.string_utils as string_utils
import Dependencies.Logger.logger_config as logger_config

from Dependencies.Common.singleton import Singleton

from m3u import M3uEntry
import m3u


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
    def __init__(self):
        self._by_title_filters : list[M3uEntryByTitleFilter] = []
        self._by_title_filters.append(TitleContainsExactlyFilter(True, "Contains Exactly (case sensitive)"))
        self._by_title_filters.append(TitleContainsExactlyFilter(False, "Contains Exactly (case NOT sensitive)")) 

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
    def __init__(self, entry_type = M3uEntry.EntryType):
        super().__init__("Any" if entry_type is None else str(entry_type.value))
        self._entry_type:M3uEntry = entry_type

    def match_m3u(self, m3u_entry:M3uEntry):
        if self._entry_type is None:
            return True
        return self._entry_type == m3u_entry.type
    

class M3uEntryByTitleFilter(M3uEntryFilter):
    """ base class """
    def __init__(self, case_sensitive:bool, label:str):
        super().__init__(label)
        self._case_sensitive:bool = case_sensitive
    
    @property
    def case_sensitive(self):
        return self._case_sensitive

    @case_sensitive.setter
    def case_sensitive(self, value):
        self._case_sensitive = value

      
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
        

    
