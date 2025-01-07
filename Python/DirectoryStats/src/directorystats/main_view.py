# -*-coding:Utf-8 -*
""" Main View """

import tkinter
import importlib

from tkinter import (
  filedialog, 
  ttk,
  Frame
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import application

from logger import logger_config

from explorerview import ExplorerViewFrame
from detailview import DetailViewFrame

class DirectoryStatsMainView (tkinter.Frame):
    """ Main view of application """

    def __init__(self, top_level_window: tkinter.Tk | tkinter.Toplevel)->None:
        super().__init__()
    
        self._top_level_window:tkinter.Tk = top_level_window
        top_level_window.title("Directory Stats")
        
        paned_window = tkinter.PanedWindow(self,
            background="cyan",
            bd=4,
            orient=tkinter.HORIZONTAL,
            sashrelief=tkinter.RAISED,
            sashwidth=4,
            showhandle=False,
            sashpad=5,
            sashcursor="sb_h_double_arrow")

        paned_window.pack(fill="both", expand=True)

        self._directory_stats_application: application.DirectoryStatsApplication

        self._create_menu_bar()

        self._explorer_view = ExplorerViewFrame(paned_window, self, top_level_window)
        self._detail_view = DetailViewFrame(paned_window, self, top_level_window)

        paned_window.add(self._explorer_view, minsize=100)
        paned_window.add(self._detail_view, minsize=100)

        sashframe = tkinter.Frame(paned_window, background="blue")
        sashframe.place(relx=0.5, rely=0.5, relwidth=0.02, relheight=1.0, anchor="center")

        sashlabel = tkinter.Label(sashframe, background="red")
        sashlabel.pack(fill="both", expand=True)



        self.bind("<B1-Motion>", self.on_dragged)
        #self._create_main_frame()

    def on_dragged(self, event:tkinter.Event)->None:
        """ on_dragged """
        print(f"on_dragged {event}")
        sash_x = event.x
        if sash_x > 10 and sash_x < root.winfo_width() - 10:
            #sashframe.place(x=sash_x, y=0, relwidth=0.02, relheight=1.0, anchor="center")
            #paned_window.sash_place(0, sash_x, 0)
            pass
            
    def create_tab_list_details(self)->None:
        """ Create tab details """
        #self._tab_list_details = ExplorerViewTab(self, self._tab_control)
        #self._tab_control.add(self._tab_list_details, text ='List detail')


        
    def _create_menu_bar(self)->None:

        menu_bg = "black"
        menu_fg = "lightgrey"


        submenu_bg = "black"
        submenu_fg = "lightgrey"

        menu_bar = tkinter.Menu(self)
        self._top_level_window.config(menu=menu_bar)
        menu_bar.config(
            font=("Courier", 11),
            bg=menu_bg,
            fg=menu_fg,
            borderwidth=6,
            relief=tkinter.RAISED
        )

        file_menu = tkinter.Menu(
            menu_bar,
            tearoff=0,
            font=("Courier New", 10),
            bg=submenu_bg,
            fg=submenu_fg
        )
        menu_bar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Open..", accelerator="Ctrl+o", command=self.menu_select_and_scan_directory)
        self.bind_all("<Control-o>", lambda x: self.menu_select_and_scan_directory())


    def menu_select_and_scan_directory(self)->None:
        """ Select and open new file """
        logger_config.print_and_log_info("open menu executed")
        
        directory_path = filedialog.askdirectory()
        directory_path_name = str(directory_path)
        logger_config.print_and_log_info("Directory chosen:" + str(directory_path_name))

        if directory_path:
            self._directory_stats_application.select_root_directory(directory_path_name)

        else:
            logger_config.print_and_log_info("Menu select_and_scan_directory cancelled")

    
if __name__ == "__main__":
    # sys.argv[1:]
    main = importlib.import_module("main")
    main.main()

