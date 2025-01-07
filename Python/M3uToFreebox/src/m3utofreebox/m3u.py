""" Details view """

# -*-coding:Utf-8 -*

from itertools import count
import importlib
from enum import Enum

from typing import TYPE_CHECKING

from common import string_utils, file_name_utils, constants
from logger import logger_config

if TYPE_CHECKING:
    from m3u_search_filters import M3uEntryByTitleFilter, M3uEntryByTypeFilter


MRU_FIRST_LINE = "#EXTM3U"
M3U_ENTRY_FIRST_LINE_BEGIN = "#EXTINF"


class M3uEntryStringDefinition:
    """ To build M3uEntry """
    def __init__(self) -> None:
        self._line1:str = ""
        self._line2:str = ""

    @property
    def line1(self)->str:
        """ getter _line1 """
        return self._line1

    @line1.setter
    def line1(self, value:str)->None:
        self._line1 = value

    @property
    def line2(self)->str:
        """ line2 """
        return self._line2

    @line2.setter
    def line2(self, value:str)->None:
        self._line2 = value

class M3uEntry:
    """ M3u entry"""

    class EntryType(Enum):
        DOWNLOADABLE = "File"
        CHANNEL = "Channel"
    

    _ids:count = count(0)

    def __init__(self, current_m3u_entry_lines_definition: M3uEntryStringDefinition) -> None:

        self._id:int = next(self._ids)
        self._link:str = current_m3u_entry_lines_definition.line2

        self._line1 = current_m3u_entry_lines_definition.line1

        self._tvg_id = self._decode_field(self._line1, "tvg-id")
        self._tvg_name = self._decode_field(self._line1, "tvg-name")
        self._tvg_logo = self._decode_field(self._line1, "tvg-logo")
        self._group_title = self._decode_field(self._line1, "group-title")
        self._original_raw_title:str = self._line1.split('"')[len(self._line1.split('"'))-1][1:]
        
        self._last_computed_file_size:int|None = None
        self._last_error_when_trying_to_retrieve_size:str|None = None

        self._compute_title_as_valid_file_name()
        self._compute_cleaned_title()
        self._compute_extension()
        self._compute_type()

        self._m3u_entries = M3uEntriesLibrary()

        self._m3u_entries.add(self)
        
    def _compute_type(self)->None:
        if self._file_extension is not None:
            self._type = M3uEntry.EntryType.DOWNLOADABLE
        else:
            self._type = M3uEntry.EntryType.CHANNEL

    def _compute_extension(self)->None:
        """ Compute extension """
        
        #http://vdevoxtv.top:2103/movie/412910643GRB/dn5QFp3/24950.mp4
        #http://veavoxtv.top:2103/412910643GRB/dn5QFp3/37744
        #http://vedvoxtv.top:2103/series/412910643GRB/dn5QFp3/57996.mkv
        self._file_extension:str = file_name_utils.file_extension_from_full_path(self._link)
        



    def _compute_title_as_valid_file_name(self)->None:
        """ Remove special caracters """
        self._title_as_valid_file_name:str = string_utils.format_filename(self._original_raw_title, True)
               
    def _compute_cleaned_title(self)->None:
        """ Remove special caracters """
        self._cleaned_title:str = self._original_raw_title
        self._cleaned_title = self._cleaned_title.replace(chr(9600),"")
        self._cleaned_title = self._cleaned_title.replace(chr(9604),"")

    def _decode_field(self, line:str, field_name:str) -> str:
        field_content = line.split(field_name)[1].split('"')[1]
        return field_content

    def can_be_downloaded(self)->bool:
        """ can_be_downloaded """
        return self._type == M3uEntry.EntryType.DOWNLOADABLE

    @property
    def type(self) -> EntryType:
        """ _type getter """
        return self._type

    @property
    def link(self)->str:
        """ _link getter """
        return self._link

    @property
    def file_extension(self)->str:
        """ file_extension getter """
        return self._file_extension

    @property
    def cleaned_title(self)->str:
        """ getter _cleaned_title """
        return self._cleaned_title

    @property
    def tvg_id(self)->str:
        """ getter _tvg_id """
        return self._tvg_id

    @property
    def tvg_name(self)->str:
        """ getter tvg_name """
        return self._tvg_name

    @property
    def tvg_logo(self)->str:
        """ getter _tvg_logo """
        return self._tvg_logo

    @property
    def id(self)->int:
        """ getter _id """
        return self._id

    @property
    def group_title(self)->str:
        """ getter _group_title """
        return self._group_title

    def get_file_size_to_display(self)->int|str:
        """ get_file_size_to_display """
        if self.can_be_downloaded():
            if self._last_error_when_trying_to_retrieve_size is not None:
                return self._last_error_when_trying_to_retrieve_size

            return self._last_computed_file_size if self._last_computed_file_size is not None else ""
        else:
            return "NA"

    def set_last_computed_file_size(self, value:int)->None:
        """ set_last_computed_file_size setter """
        self._last_computed_file_size = value

    @property
    def original_raw_title(self)-> str:
        """ getter _title """
        return self._original_raw_title

    @original_raw_title.setter
    def original_raw_title(self, value:str)->None:
        self._original_raw_title = value

    def last_error_when_trying_to_retrieve_size(self, value:str|None)->None:
        """ Setter last_error_when_trying_to_retrieve_size """
        self._last_error_when_trying_to_retrieve_size = value
        
    @property
    def title_as_valid_file_name(self)->str:
        """ getter _title_as_valid_file_name """
        return self._title_as_valid_file_name

    def __str__(self)->str:
        return "M3u Entry id:" + str(self.id) +  ", title:" + self.original_raw_title

class M3uFileParser:
    """ Parse m3u file """
    def __init__(self) -> None:
        pass
    
    def parse_file(self,file_path:str) -> list[M3uEntry]:
        """ parse file """
        m3u_entries: list[M3uEntry] = []
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            current_m3u_entry_string_definition = M3uEntryStringDefinition()
            lines = content.split(constants.END_LINE_CHARACTER_IN_TEXT_FILE)
            for line in lines:
                if MRU_FIRST_LINE == line:
                    continue
                                
                if line.startswith(M3U_ENTRY_FIRST_LINE_BEGIN):
                    current_m3u_entry_string_definition = M3uEntryStringDefinition()
                    current_m3u_entry_string_definition.line1 = line
                    
                if not line.startswith(M3U_ENTRY_FIRST_LINE_BEGIN):
                    current_m3u_entry_string_definition.line2 = line
                    m3u_entry = M3uEntry(current_m3u_entry_string_definition)
                    m3u_entries.append(m3u_entry)
                    logger_config.logging.debug("M3u entry created: " + str(m3u_entry))

        logger_config.print_and_log_info("File " + file_path + " parsed. " + str(len(m3u_entries)) + " M3u entries found")
        return m3u_entries



class M3uEntriesLibrary:
    """ M3u library"""

    def __init__(self) -> None:
        self._m3u_entries: list[M3uEntry] = []

    @property
    def m3u_entries(self) -> list[M3uEntry]:
        """ Getter """
        return self._m3u_entries

    def add(self, m3u_entry:M3uEntry) -> None:
        """ add m3u to library """
        self._m3u_entries.append(m3u_entry)

    def get_m3u_entry_by_id(self, m3u_entry_id:int) -> M3uEntry:
        """ get_m3u_entry_by_id """
        m3u_entries_with_id = [m3u_entry for m3u_entry in self._m3u_entries if m3u_entry.id == m3u_entry_id]
        logger_config.logging.debug("Found " + str(len(m3u_entries_with_id)) + " entries matching id:" + str(m3u_entry_id))
        if(len(m3u_entries_with_id) != 1):
            raise RuntimeError("Found " + str(len(m3u_entries_with_id)) + " entries matching id:" + str(m3u_entry_id))
        
        m3u_entry = m3u_entries_with_id[0]
        logger_config.logging.debug("M3u entry for id:" + str(m3u_entry_id) + " : " + str (m3u_entry))
        return m3u_entry
        
    def get_m3u_entries_with_filter(self, typed_text: str, selected_title_filter:'M3uEntryByTitleFilter', selected_type_filter:'M3uEntryByTypeFilter', ignore_case:bool, ignore_diacritics:bool) -> list[M3uEntry]:
        """ filter list of m3u """
        ret: list[M3uEntry] = []
        
        if str is None:
            return self._m3u_entries

        for m3u_entry in self._m3u_entries:
            if selected_type_filter.match_m3u(m3u_entry) and selected_title_filter.match_m3u(m3u_entry, typed_text, ignore_case, ignore_diacritics):
                ret.append(m3u_entry)

        logger_config.print_and_log_info("Number of entries with typed text:" + typed_text + ": " + str(len(ret)))
        return ret
    
if __name__ == "__main__":
    # sys.argv[1:]
    main = importlib.import_module("main")
    main.main()
