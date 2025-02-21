# -*-coding:Utf-8 -*

from warnings import deprecated
import importlib


from logger import logger_config
from common import file_size_utils

import m3u
import xspf

import param

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_view import M3uToFreeboxMainView


class M3uToFreeboxApplication:
    """Application"""

    def __init__(self, main_view: "M3uToFreeboxMainView") -> None:

        self._m3u_library: m3u.M3uEntriesLibrary = m3u.M3uEntriesLibrary()

        self._main_view: "M3uToFreeboxMainView" = main_view

    def get_to_be_downloaded_movie_infos_by_id_str(self, destination_directory: str, m3u_entry_id: str):
        m3u_entry_id_int = int(m3u_entry_id)
        m3u_entry: m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id_int)
        if m3u_entry.can_be_downloaded():
            file_destination_full_path = (
                destination_directory + "\\" + m3u_entry.title_as_valid_file_name + m3u_entry.file_extension
            )
            return m3u_entry.link, file_destination_full_path
        else:
            return None, None

    @deprecated("Just for tests")
    def load_fake(self, m3u_entry_id_str: str) -> bool:
        """load_fake"""
        m3u_entry_id_int = int(m3u_entry_id_str)
        m3u_entry: m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id_int)
        m3u_entry.set_last_computed_file_size(105)
        return True

    def load_m3u_entry_size_by_id_str(self, m3u_entry_id_str: str) -> bool:
        """load_m3u_entry_size_by_id_str"""
        m3u_entry_id_int = int(m3u_entry_id_str)
        m3u_entry: m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id_int)

        if m3u_entry.can_be_downloaded():
            result, length_or_error = file_size_utils.get_url_file_size(m3u_entry.link)

            if result:
                m3u_entry.set_last_computed_file_size(
                    file_size_utils.convert_bits_to_human_readable_size(length_or_error)
                )
                return True

            else:
                logger_config.print_and_log_error(f"Error code: {length_or_error} for {m3u_entry}")
                m3u_entry.last_error_when_trying_to_retrieve_size = f"Error! {length_or_error}"

        return False

    def create_xspf_file_by_id_str(self, destination_directory: str, m3u_entry_id: str):
        m3u_entry_id_int = int(m3u_entry_id)
        self.create_xspf_file_by_id(destination_directory, m3u_entry_id_int)

    def create_xspf_file_by_id(self, destination_directory: str, m3u_entry_id: int):

        m3u_entry: m3u.M3uEntry = self.m3u_library.get_m3u_entry_by_id(m3u_entry_id)

        xspf_file_content = xspf.XspfFileContent(m3u_entry.cleaned_title, m3u_entry.link)
        xsp_file_creator = xspf.XspfFileCreator()
        xsp_file_creator.write(
            xspf_file_content, destination_directory, m3u_entry.title_as_valid_file_name + ".xspf", True
        )

    def reset_library(self):
        self._m3u_library = m3u.M3uEntriesLibrary()

    def load_file(self, file_path, save_path_of_m3u_file: bool = True):
        """Load file"""
        logger_config.print_and_log_info("Load file:" + file_path)

        m3u_file_parser = m3u.M3uFileParser()
        for m3u_entry in m3u_file_parser.parse_file(file_path):
            self._m3u_library.add(m3u_entry)

        if save_path_of_m3u_file:
            with open(
                param.PATH_OF_FILE_LISTING_LAST_M3U_FILE_LOADED, "w", encoding="utf-8"
            ) as file_listing_last_m3u_file_loaded:
                file_listing_last_m3u_file_loaded.write(f"{file_path}")

    def load_last_loaded_m3u_file(self) -> bool:
        """load_last_loaded_m3u_file"""
        try:
            with open(
                param.PATH_OF_FILE_LISTING_LAST_M3U_FILE_LOADED, "r", encoding="utf-8"
            ) as file_listing_last_m3u_file_loaded:
                content = file_listing_last_m3u_file_loaded.read()
                logger_config.print_and_log_info(f"Last loaded m3u file:{content}")
                self.load_file(content, False)
                return True

        except FileNotFoundError:
            logger_config.print_and_log_info(f"Could not open file:{param.PATH_OF_FILE_LISTING_LAST_M3U_FILE_LOADED}")
            return False

    @property
    def m3u_library(self) -> m3u.M3uEntriesLibrary:
        return self._m3u_library

    @m3u_library.setter
    def m3u_library(self, value: m3u.M3uEntriesLibrary):
        self._m3u_library = value


if __name__ == "__main__":
    # sys.argv[1:]
    main = importlib.import_module("main")
    main.main()
