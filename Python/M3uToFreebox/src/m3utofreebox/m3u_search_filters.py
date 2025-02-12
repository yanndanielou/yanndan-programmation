""" Filters to search M3u entry by criteria """

# -*-coding:Utf-8 -*

from abc import abstractmethod
import re

import importlib

from common import singleton, tokenization_string, language_utils, list_utils

from m3u import M3uEntry


class M3uEntryFilter:
    """base class"""

    def __init__(self, label: str):
        self._label: str = label

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value


class M3uFiltersManager(metaclass=singleton.Singleton):
    """Manager of m3u filters"""

    def __init__(self):
        self._by_title_filters: list[M3uEntryByTitleFilter] = []
        self._by_title_filters.append(TitleContainsExactlyFilter(label="Contains Exactly"))
        self._by_title_filters.append(TitleContainsAllWordsFilter(whole_words=False, label="Contains all words"))
        self._by_title_filters.append(
            TitleContainsAllWordsFilter(whole_words=True, label="Contains all words (whole worlds)")
        )
        self._by_title_filters.append(TitleMatchesFilterTextRegex(label="Matches Regex"))

        self._by_type_filters: list[M3uEntryByTypeFilter] = []
        self._by_type_filters.append(M3uEntryByTypeFilter(None))
        for e in M3uEntry.EntryType:
            self._by_type_filters.append(M3uEntryByTypeFilter(e))

    @property
    def by_title_filters(self):
        """Getter filters"""
        return self._by_title_filters

    @by_title_filters.setter
    def by_title_filters(self, value):
        self._by_title_filters = value

    @property
    def by_type_filters(self):
        """Getter filters"""
        return self._by_type_filters

    @by_type_filters.setter
    def by_type_filters(self, value):
        self._by_type_filters = value


class M3uEntryByTypeFilter(M3uEntryFilter):
    def __init__(self, entry_type: M3uEntry.EntryType):
        super().__init__("Any" if entry_type is None else str(entry_type.value))
        self._entry_type: M3uEntry.EntryType = entry_type

    def match_m3u(self, m3u_entry: M3uEntry) -> bool:
        if self._entry_type is None:
            return True
        return self._entry_type == m3u_entry.type


class M3uEntryByTitleFilter(M3uEntryFilter):
    """base class"""

    def __init__(self, label: str):
        super().__init__(label)

    @abstractmethod
    def match_m3u(self, m3u_entry: M3uEntry, filter_text: str, ignore_case: bool, ignore_diacritics: bool) -> bool:
        """Check if match m3u"""
        raise NotImplementedError()


class TitleContainsExactlyFilter(M3uEntryByTitleFilter):
    """TitleContainsExactlyFilter"""

    def __init__(self, label: str):
        super().__init__(label)

    def match_m3u(self, m3u_entry: M3uEntry, filter_text: str, ignore_case: bool, ignore_diacritics: bool) -> bool:
        if not ignore_case:
            return filter_text in m3u_entry.original_raw_title
        return filter_text.lower() in m3u_entry.original_raw_title.lower()


class TitleMatchesFilterTextRegex(M3uEntryByTitleFilter):
    """TitleMatchesFilterTextRegex"""

    def __init__(self, label):
        super().__init__(label)

        self._filter_text = None
        self._regex_pattern = None

    def match_m3u(self, m3u_entry: M3uEntry, filter_text: str, ignore_case: bool, ignore_diacritics: bool):

        if not ignore_case:
            filter_text = filter_text.lower()

        if self._filter_text != filter_text:
            self._filter_text = filter_text
            self._regex_pattern = re.compile(filter_text)

        m3u_entry_original_raw_title = (
            m3u_entry.original_raw_title if not ignore_case else m3u_entry.original_raw_title.lower()
        )

        match = self._regex_pattern.match(m3u_entry_original_raw_title)
        return match is not None


class TitleContainsAllWordsFilter(M3uEntryByTitleFilter):
    """TitleContainsExactlyFilter"""

    def __init__(self, whole_words: bool, label: str):
        super().__init__(label)
        self._whole_words = whole_words

        self._filter_text = None
        self._filter_text_language = None
        self._filter_text_words = None

    def recompute_filter_text_words_and_language(self, filter_text: str):
        if self._filter_text != filter_text:
            self._filter_text = filter_text
            self._filter_text_language = language_utils.get_full_language_name(
                language_utils.detect_language_with_langid(filter_text)
            )
            self._filter_text_words = tokenization_string.tokenize_text_with_nltk_regexp_tokenizer(filter_text)

    def match_m3u(self, m3u_entry: M3uEntry, filter_text: str, ignore_case: bool, ignore_diacritics: bool):

        if not self._whole_words:
            filter_text_words = tokenization_string.tokenize_text_with_nltk_regexp_tokenizer(filter_text)
            for filter_word in filter_text_words:
                title_contains_exactly_word = TitleContainsExactlyFilter(not ignore_case, self.label + filter_word)
                if not title_contains_exactly_word.match_m3u(m3u_entry, filter_word, ignore_case, ignore_diacritics):
                    return False

            return True

        else:
            m3u_entry_original_raw_title = (
                m3u_entry.original_raw_title if not ignore_case else m3u_entry.original_raw_title.lower()
            )
            if not not ignore_case:
                filter_text = filter_text.lower()

            self.recompute_filter_text_words_and_language(filter_text)

            self._m3u_entry_original_words = tokenization_string.tokenize_text_with_nltk_regexp_tokenizer(
                m3u_entry_original_raw_title
            )

            return list_utils.are_all_elements_of_list_included_in_list(
                self._filter_text_words, self._m3u_entry_original_words
            )

    def tdoto(self, tt, ff):
        return tt + ff


if __name__ == "__main__":
    # sys.argv[1:]
    main = importlib.import_module("main")
    main.main()
