# -*-coding:Utf-8 -*

import sys
import os

#sys.path.insert(1, os.getcwd())
#sys.path.append("D:/GitHub/yanndanielou-programmation/Python/Logger")
#sys.path.append("../Logger")

#import logger_config

import Dependencies.Logger.logger_config as logger_config
import Dependencies.Common.date_time_formats as date_time_formats

import tkinter

import importlib

import time

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_view import DirectoryStatsMainView



from tkinter import (
  filedialog, 
  simpledialog, 
  messagebox, 
  scrolledtext, 
  Menu,
  colorchooser,
  ttk
  )


class DetailViewFrame(ttk.Frame):
    """ DetailViewFrame """
    
    def __init__(self, parent:'DirectoryStatsMainView'):
        super().__init__()
        
        self._paddings = {'padx': 5, 'pady': 5}

        self._parent:'DirectoryStatsMainView' = parent
        
        self._tab_control = ttk.Notebook(self)
        #self.create_tab_list_details()
        self._tab_control.pack(expand = 1, fill ="both")

        self._tab_control.pack()
    
    
if __name__ == "__main__":
    main = importlib.import_module("main")
    main.main()
