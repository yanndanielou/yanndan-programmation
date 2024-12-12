""" Details view """

# -*-coding:Utf-8 -*

from itertools import count
import importlib

import Dependencies.Common.string_utils as string_utils

import Dependencies.Logger.logger_config as logger_config
import Dependencies.Common.Constants

#from m3u_search_filters import M3uEntryByTitleFilter

MRU_FIRST_LINE = "#EXTM3U"
M3U_ENTRY_FIRST_LINE_BEGIN = "#EXTINF"


class M3uEntryStringDefinition:
    """ To build M3uEntry """
    def __init__(self) -> None:
        self._line1 = None
        self._line2 = None

    @property
    def line1(self):
        """ getter """
        return self._line1

    @line1.setter
    def line1(self, value):
        self._line1 = value

    @property
    def line2(self):
        """ line2 """
        return self._line2

    @line2.setter
    def line2(self, value):
        self._line2 = value

class M3uEntry:
    """ M3u entry"""

    _ids = count(0)

    def __init__(self, current_m3u_entry_lines_definition: M3uEntryStringDefinition) -> None:

        self._id = next(self._ids)
        self._link = current_m3u_entry_lines_definition.line2
        self._line1 = current_m3u_entry_lines_definition.line1

        self._tvg_id = self.decode_field(self._line1, "tvg-id")
        self._tvg_name = self.decode_field(self._line1, "tvg-name")
        self._tvg_logo = self.decode_field(self._line1, "tvg-logo")
        self._group_title = self.decode_field(self._line1, "group-title")
        self._title:str = self._line1.split('"')[len(self._line1.split('"'))-1][1:]

        self._compute_title_as_valid_file_name()

        self._m3u_entries = M3uEntriesLibrary()

        self._m3u_entries.add(self)
        

    def _compute_title_as_valid_file_name(self):
        """ Remove special caracters """
        self._title_as_valid_file_name:str = string_utils.format_filename(self._title, True)
               

    def decode_field(self, line, field_name) -> str:
        field_content = line.split(field_name)[1].split('"')[1]

        return field_content


    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, value):
        self._link = value

    @property
    def line1(self):
        """ getter _line1 """
        return self._line1

    @line1.setter
    def line1(self, value):
        self._line1 = value

    @property
    def tvg_id(self):
        """ getter _tvg_id """
        return self._tvg_id

    @tvg_id.setter
    def tvg_id(self, value):
        self._tvg_id = value

    @property
    def tvg_name(self):
        """ getter tvg_name """
        return self._tvg_name

    @tvg_name.setter
    def tvg_name(self, value):
        self._tvg_name = value

    @property
    def tvg_logo(self):
        """ getter _tvg_logo """
        return self._tvg_logo

    @tvg_logo.setter
    def tvg_logo(self, value):
        self._tvg_logo = value
        
    @property
    def id(self):
        """ getter _id """
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def group_title(self):
        """ getter _group_title """
        return self._group_title

    @group_title.setter
    def group_title(self, value):
        self._group_title = value

    @property
    def title(self):
        """ getter _title """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        
    @property
    def title_as_valid_file_name(self):
        """ getter _title_as_valid_file_name """
        return self._title_as_valid_file_name

    def __str__(self):
        return "M3u Entry id:" + str(self.id) +  ", title:" + self.title

class M3uFileParser:
    """ Parse m3u file """
    def __init__(self) -> None:
        pass
    
    def parse_file(self,file_path) -> list[M3uEntry]:
        """ parse file """
        m3u_entries: list[M3uEntry] = []
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            current_m3u_entry_string_definition = M3uEntryStringDefinition()
            lines = content.split(Dependencies.Common.Constants.end_line_character_in_text_file)
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
        
    def get_m3u_entry_by_id(self, m3u_entry_id:int):
        m3u_entries_with_id = [m3u_entry for m3u_entry in self._m3u_entries if m3u_entry.id == m3u_entry_id]
        logger_config.logging.debug("Found " + str(len(m3u_entries_with_id)) + " entries matching id:" + str(m3u_entry_id))
        if(len(m3u_entries_with_id) != 1):
            raise Exception("Found " + str(len(m3u_entries_with_id)) + " entries matching id:" + str(m3u_entry_id))
        
        m3u_entry = m3u_entries_with_id[0]
        logger_config.logging.debug("M3u entry for id:" + str(m3u_entry_id) + " : " + str (m3u_entry))
        return m3u_entry
        
    def get_m3u_entries_with_filter(self, typed_text: str, selected_filter) -> list[M3uEntry]:
        """ filter list of m3u """
        ret: list[M3uEntry] = []
        
        if str is None:
            return self._m3u_entries
        
        for m3u_entry in self._m3u_entries:
            if selected_filter.match_m3u(m3u_entry, typed_text):
                ret.append(m3u_entry)
        
        logger_config.print_and_log_info("Number of entries with typed text:" + typed_text + ": " + str(len(ret)))
        return ret
        
    
if __name__ == "__main__":
    # sys.argv[1:]
    main = importlib.import_module("main")
    main.main()

