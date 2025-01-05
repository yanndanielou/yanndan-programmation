# -*-coding:Utf-8 -*


import tkinter
import importlib

from tkinter import (
  filedialog, 
  ttk
)

from Dependencies.Logger import logger_config

from detailsview import DetailsViewTab

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import M3uToFreeboxApplication

class M3uToFreeboxMainView (tkinter.Tk):
    """ Main view of application """

    def __init__(self)->None:
        super().__init__()        

        self.title("M3U to Freebox")

        self._m3u_to_freebox_application: 'M3uToFreeboxApplication'|None = None


        self._create_menu()
        self._tab_control = ttk.Notebook(self)
        self.create_tab_list_details()
        self.create_tab_empty()
        self._tab_control.pack(expand = 1, fill ="both")

        self._tab_control.pack()
       
        #self._create_main_frame()


    def create_tab_list_details(self)->None:
        """ Create tab details """
        self._tab_list_details = DetailsViewTab(self, self._tab_control)
        self._tab_control.add(self._tab_list_details, text ='List detail')

    def create_tab_empty(self)->None:
        self._tab_empty = ttk.Frame(self._tab_control)
        self._tab_control.add(self._tab_empty, text ='Empty')

        
    def _create_menu(self)->None:

        menu_bg = "black"
        menu_fg = "lightgrey"


        submenu_bg = "black"
        submenu_fg = "lightgrey"

        menu_bar = tkinter.Menu(self)
        self.config(menu=menu_bar)
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

        file_menu.add_command(label="Open..", accelerator="Ctrl+o", command=self.menu_select_and_open_file)
        self.bind_all("<Control-o>", lambda x: self.menu_select_and_open_file())

        file_menu.add_command(label="Open last m3u file loaded", accelerator="Ctrl+l", command=self.menu_open_last_m3u_file_loaded)
        self.bind_all("<Control-l>", lambda x: self.menu_open_last_m3u_file_loaded())



    def menu_open_last_m3u_file_loaded(self):
        """ Select and open new file """
        logger_config.print_and_log_info("menu_open_last_m3u_file_loaded")
        
        if self._m3u_to_freebox_application.load_last_loaded_m3u_file():
            self._tab_list_details.fill_m3u_entries()


    def menu_select_and_open_file(self):
        """ Select and open new file """
        logger_config.print_and_log_info("open menu executed")

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("M3u", "*.m3u*"),
            ]
        )
        
        if file_path:
            logger_config.print_and_log_info("Open file:" + file_path)

            self._m3u_to_freebox_application.load_file(file_path, True)
            self._tab_list_details.fill_m3u_entries()
            
        else:
            logger_config.print_and_log_info("Open menu cancelled")


    @property
    def m3u_to_freebox_application(self)->'M3uToFreeboxApplication':
        """ Getter for _m3u_to_freebox_application """
        return self._m3u_to_freebox_application

    @m3u_to_freebox_application.setter
    def m3u_to_freebox_application(self, value:'M3uToFreeboxApplication')->None:
        self._m3u_to_freebox_application = value

    
if __name__ == "__main__":
    # sys.argv[1:]
    main = importlib.import_module("main")
    main.main()

