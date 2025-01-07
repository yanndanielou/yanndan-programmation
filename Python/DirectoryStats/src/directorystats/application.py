# -*-coding:Utf-8 -*

from warnings import deprecated


import param

from typing import TYPE_CHECKING
import importlib

import io

import urllib.request
import urllib.error

import urllib.request
from urllib.error import URLError, HTTPError

from logger import logger_config
from common import date_time_formats, file_size_utils

if TYPE_CHECKING:
    from main_view import DirectoryStatsMainView


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