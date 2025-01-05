# -*-coding:Utf-8 -*

import sys
import os

import tkinter as tk
from pathlib import Path
from tkinter import ttk


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

from enum import Enum


class ExplorerViewFrame(ttk.Frame):
    """ ExplorerViewFrame """
    
    def __init__(self, parent:'DirectoryStatsMainView', top_level_window: tkinter.Tk | tkinter.Toplevel):
        super().__init__()
        
        self._paddings = {'padx': 5, 'pady': 5}

        self._parent:'DirectoryStatsMainView' = parent    
        
                # show="tree" removes the column header, since we
        # are not using the table feature.
        self.treeview = ttk.Treeview(self, show="tree")
        self.treeview.grid(row=0, column=0, sticky="nsew")
        # Call the item_opened() method each item an item
        # is expanded.
        self.treeview.tag_bind(
            "fstag", "<<TreeviewOpen>>", self.item_opened)
        # Make sure the treeview widget follows the window
        # when resizing.
        for w in (self, top_level_window):
            w.rowconfigure(0, weight=1)
            w.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")
        # This dictionary maps the treeview items IDs with the
        # path of the file or folder.
        self.fsobjects: dict[str, Path] = {}
        self.file_image = tk.PhotoImage(file="ressources/file.png")
        self.folder_image = tk.PhotoImage(file="ressources/folder.png")
        # Load the root directory.
        self.load_tree(Path(Path(sys.executable).anchor))

    def safe_iterdir(self, path: Path) -> tuple[Path, ...] | tuple[()]:
        """
        Like `Path.iterdir()`, but do not raise on permission errors.
        """
        try:
            return tuple(path.iterdir())
        except PermissionError:
            print("You don't have permission to read", path)
            return ()

    def get_icon(self, path: Path) -> tk.PhotoImage:
        """
        Return a folder icon if `path` is a directory and
        a file icon otherwise.
        """
        return self.folder_image if path.is_dir() else self.file_image

    def insert_item(self, name: str, path: Path, parent: str = "") -> str:
        """
        Insert a file or folder into the treeview and return the item ID.
        """
        iid = self.treeview.insert(
            parent, tk.END, text=name, tags=("fstag",),
            image=self.get_icon(path))
        self.fsobjects[iid] = path
        return iid

    def load_tree(self, path: Path, parent: str = "") -> None:
        """
        Load the contents of `path` into the treeview.
        """
        for fsobj in self.safe_iterdir(path):
            fullpath = path / fsobj
            child = self.insert_item(fsobj.name, fullpath, parent)
            # Preload the content of each directory within `path`.
            # This is necessary to make the folder item expandable.
            if fullpath.is_dir():
                for sub_fsobj in self.safe_iterdir(fullpath):
                    self.insert_item(sub_fsobj.name, fullpath / sub_fsobj, child)

    def load_subitems(self, iid: str) -> None:
        """
        Load the content of each folder inside the specified item
        into the treeview.
        """
        for child_iid in self.treeview.get_children(iid):
            if self.fsobjects[child_iid].is_dir():
                self.load_tree(self.fsobjects[child_iid],
                            parent=child_iid)

    def item_opened(self, _event: tk.Event) -> None:
        """
        Handler invoked when a folder item is expanded.
        """
        # Get the expanded item.
        iid = self.treeview.selection()[0]
        # If it is a folder, loads its content.
        self.load_subitems(iid)


    
if __name__ == "__main__":
    main = importlib.import_module("main")
    main.main()
