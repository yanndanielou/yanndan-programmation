""" Filters to search M3u entry by criteria """
# -*-coding:Utf-8 -*

from Dependencies.Common.singleton import Singleton
from Dependencies.Logger import logger_config


from tkinter import (
  filedialog
  )

class DestinationsFolders(metaclass=Singleton):
    """ Manager of m3u filters"""
    def __init__(self):
        self._destinations_folders:list[tuple[str, str]] = [DestinationFolder("Freebox", "\\\\Freebox_Server\\NO NAME\\M3U_Playlist"),DestinationFolder("Local", "D:\\"), DestinationFolder("..", None)]


    def add_destination(self, name:str, path:str):
        """ Add destinations """
        self._destinations_folders.append((name, path))
        
    @property
    def destinations_folders(self):
        """ Getter filters """
        #return self._destinations_folders
        return self._destinations_folders

class DestinationFolder():
    def __init__(self, label, path):
        self._label = label
        self._path = path
    
    def get_path(self):
        if self._path is not None:
            return self._path
        
        else:
            directory_path:filedialog.Directory = filedialog.askdirectory()
            directory_path_name = str(directory_path)
            logger_config.print_and_log_info("Directory chosen:" + str(directory_path_name))

            if directory_path_name != "":
                DestinationsFolders().destinations_folders.append(directory_path_name)
                return directory_path_name
            else:
                logger_config.print_and_log_info("No directory chosen")
                return None