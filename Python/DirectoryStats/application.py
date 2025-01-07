# -*-coding:Utf-8 -*

from warnings import deprecated

import Dependencies.Logger.logger_config as logger_config
import Dependencies.Common.date_time_formats as date_time_formats
import Dependencies.Common.file_size_utils as file_size_utils


import param

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_view import DirectoryStatsMainView
import importlib

import io

import urllib.request
import urllib.error

import urllib.request
from urllib.error import URLError, HTTPError

class DirectoryStatsApplication:
    """ Application """

    def __init__(self, mainview:'DirectoryStatsMainView'):
        self._main_view:'DirectoryStatsMainView' = mainview


    def select_root_directory(self, root_directory_path:str)->None:
        """ select_root_directory """
        pass


if __name__ == "__main__":
    # sys.argv[1:]
    main = importlib.import_module("main")
    main.main()