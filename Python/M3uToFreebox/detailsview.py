# -*-coding:Utf-8 -*

""" https://tkdocs.com/tutorial/firstexample.html """

import sys
import os

#sys.path.insert(1, os.getcwd())
#sys.path.append("D:/GitHub/yanndanielou-programmation/Python/Logger")
#sys.path.append("../Logger")

#import logger_config

import Dependencies.Logger.logger_config as logger_config
import Dependencies.Common.date_time_formats as date_time_formats

from destinations import DestinationsFolders, DestinationFolder

import tkinter

import importlib

import time

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from m3u_search_filters import M3uEntryByTitleFilter, M3uEntryByTypeFilter

import m3u
from m3u_search_filters import M3uFiltersManager


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

class Action(Enum):
    CREATE_XSPF_FILE = "Create xspf file"
    DONWLOAD_MOVIE= "Download movie"
    
class DetailsViewTab(ttk.Frame):

    
    def __init__(self, parent, tab_control):
        super().__init__(tab_control)
        
        self._paddings = {'padx': 5, 'pady': 5}

        import main_view
        self._parent:main_view.M3uToFreeboxMainView = parent
        
        self._by_title_filters:list[M3uEntryByTitleFilter] = M3uFiltersManager().by_title_filters

        self._by_type_filters:list[M3uEntryByTypeFilter] = M3uFiltersManager().by_type_filters
    
        self._create_view()
        self._create_context_menu()

        self._title_filter_text_content:str = None
        
        #self._organize_widgets()

    def _create_filter_frame(self):
        """ Filter """

        self._filter_frame =tkinter.LabelFrame(self, text="Filters")    
        self._filter_frame.grid(row= 0, column=0, padx=20, pady=10)
        
        self._filter_input_text = tkinter.Entry(self._filter_frame,font=('verdana',14))
        self._filter_input_text.bind("<KeyRelease>", self.filter_updated)
        self._filter_input_text.grid(row= 0, column=0, padx=20, pady=10)
        
        # padding for widgets using the grid layout
        paddings = {'padx': 5, 'pady': 5}
        self._create_title_filter()
        self._create_type_filter()

    def _create_title_filter(self):
        # Filter label
        self._title_filter_option_description_label = ttk.Label(self._filter_frame, foreground='black')
        self._title_filter_option_description_label['text'] = f'Type of title filter:'
        self._title_filter_option_description_label.grid(row= 0, column=1, padx=20, pady=10)

        # Title filter
        title_filters_texts = [o.label for o in self._by_title_filters]
        # set up variable
        self._title_filter_option_var = tkinter.StringVar(self)
        # option menu
        self._title_filter_option_menu = ttk.OptionMenu(
            self._filter_frame,
            self._title_filter_option_var,
            title_filters_texts[0],
            *title_filters_texts,
            command=self.title_filter_option_changed)        
        self._title_filter_option_menu.grid(row= 0, column=2, padx=5, pady=10)


    def _create_type_filter(self):
        # Filter label
        self._type_filter_option_description_label = ttk.Label(self._filter_frame, foreground='black')
        self._type_filter_option_description_label['text'] = f'Type of m3u:'
        self._type_filter_option_description_label.grid(row= 0, column=3, padx=20, pady=10)

        # Title filter
        type_filters_texts = [o.label for o in self._by_type_filters]

        # set up variable
        self._type_filter_option_var = tkinter.StringVar(self)
        # option menu
        self._type_filter_option_menu = ttk.OptionMenu(
            self._filter_frame,
            self._type_filter_option_var,
            type_filters_texts[0],
            *type_filters_texts,
            command=self.type_filter_option_changed)        
        self._type_filter_option_menu.grid(row= 0, column=4, padx=5, pady=10)
        

    def _create_tree_view_frame(self):
        self._tree_view_frame = tkinter.Frame(self)
        self._tree_view_frame.grid(row= 1, column=0, padx=20, pady=10)


        # Treeview Scrollbar
        self._tree_scroll_vertical = tkinter.Scrollbar(self._tree_view_frame)
        self._tree_scroll_vertical.pack(side=tkinter.RIGHT, fill=tkinter.Y)


        # Create Treeview
        self._tree_view = ttk.Treeview(self._tree_view_frame, yscrollcommand=self._tree_scroll_vertical.set, selectmode="extended", show='headings')
        
        # Pack to the screen

        #Configure the scrollbar
        self._tree_scroll_vertical.config(command=self._tree_view.yview)

        columns = ['ID','Cleaned title','Original title', 'File name', 'Group', 'type', 'Size']
        

        self._tree_view["column"] = columns

        for column in self._tree_view["column"]:
                self._tree_view.heading(column, text=column, command=lambda col2=column: \
                   self.treeview_sort_column(self._tree_view, col2, False), anchor='center')
        

        self._tree_view.column(self._tree_view["columns"][0],width=40)
 
        self._tree_view.pack()
        self._tree_scroll_vertical.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    def _create_bottom_frame(self):
        
        self._bottom_frame = tkinter.Frame(self)
        self._bottom_frame.grid(row=2, column=0, padx=20, pady=10)
        my_string_var = tkinter.StringVar()
        # set the text
        my_string_var.set("What should I learn")

        self._bottom_status_label = tkinter.Label(self._bottom_frame,font=('verdana',14),textvariable = my_string_var)  
        self._bottom_status_label.pack()
        

        

        
    def type_filter_option_changed(self, *args):
        logger_config.print_and_log_info(f'You selected: {self._type_filter_option_var.get()}')
        self.fill_m3u_entries()

        
    def title_filter_option_changed(self, *args):
        logger_config.print_and_log_info(f'You selected: {self._title_filter_option_var.get()}')
        self.fill_m3u_entries()

        
    
    def _create_context_menu(self):
        #Create context menu
        self.tree_view_context_menu: tkinter.Menu = tkinter.Menu(self, tearoff=0)
        
        self.tree_view_context_menu.add_command(label="Load file size", command=self._load_selected_file_size)
        self.tree_view_context_menu.add_separator()


        for action in Action:
            action_sub_context_menu: tkinter.Menu = tkinter.Menu(self, tearoff=0)
            self.tree_view_context_menu.add_cascade(label = action.value, menu = action_sub_context_menu)
            for destination_folder in DestinationsFolders().destinations_folders:
                action_sub_context_menu.add_command(label=action.value + " on " + destination_folder._label, command=lambda lambda_dest_folder=destination_folder, lambda_action = action: self._perform_action_on_destination_context_menu_choosen(lambda_action, lambda_dest_folder))
            
        self.tree_view_context_menu.add_separator()
        self.tree_view_context_menu.add_command(label="Show detail", command=self._open_m3u_entry_detail_popup)
        self.tree_view_context_menu.add_command(label="Clear List", command=self._clear_list)
        self.tree_view_context_menu.add_command(label="Reset List", command=self.fill_m3u_entries)
        self.tree_view_context_menu.add_command(label="Reset Library", command=self._reset_library)
        self.tree_view_context_menu.add_separator()

        def do_popup(event):
            # display the popup menu
            try:
                row_identified = self._tree_view.identify_row(event.y)
                logger_config.print_and_log_info("row_identified:" + row_identified)
                
                
                tree_view_selection = self._tree_view.selection()
                logger_config.print_and_log_info("tree_view_selection:"  + str(tree_view_selection))
        
                self.tree_view_context_menu.selection = self._tree_view.set(row_identified)
                self.tree_view_context_menu.post(event.x_root, event.y_root)
            finally:
                # make sure to release the grab (Tk 8.0a1 only)
                self.tree_view_context_menu.grab_release()
                
        self._tree_view.bind("<Button-3>", do_popup)


    def _open_m3u_entry_detail_popup(self):
        m3u_entry_line = self.tree_view_context_menu.selection
        #m3u_entry_detail_popup = detailspopup.M3uEntryDetailPopup(self, None)

    def _get_selected_m3u_entry_id_str(self)->str:
        m3u_entry_line = self.tree_view_context_menu.selection
        if len(m3u_entry_line) == 0:
            logger_config.print_and_log_info("No line selected")
            return None

        m3u_entry_id_str = m3u_entry_line['ID']  
        return m3u_entry_id_str           

    def _perform_action_on_destination_context_menu_choosen(self, action:Action, destination:DestinationFolder):

        logger_config.print_and_log_info("destination chosen: " + str(destination))
        logger_config.print_and_log_info("action chosen: " + str(action))

        m3u_entry_id_str = self._get_selected_m3u_entry_id_str()
        
        
        destination_directory = destination.get_path()
        logger_config.print_and_log_info(f"destination_directory chosen:{destination_directory} ")
    
        if m3u_entry_id_str is None:
            return
        
        if destination_directory is None:
            return
        
        
                  
  
        match action:
            case Action.DONWLOAD_MOVIE:
                self._parent.m3u_to_freebox_application.download_movie_file_by_id_str(destination_directory, m3u_entry_id_str)

            case Action.CREATE_XSPF_FILE:
                self._parent.m3u_to_freebox_application.create_xspf_file_by_id_str(destination_directory, m3u_entry_id_str)

    def _load_selected_file_size(self):
        m3u_entry_id_str = self._get_selected_m3u_entry_id_str()
        self._parent.m3u_to_freebox_application.load_m3u_entry_size_by_id_str(m3u_entry_id_str)

        m3u_entry = self._parent.m3u_to_freebox_application.m3u_library.get_m3u_entry_by_id(int(m3u_entry_id_str))
        self._tree_view.set(m3u_entry.id, column="Size", value = m3u_entry.get_file_size_to_display())

    def _create_xspf_on_destination_context_menu_choosen(self, destination):
        logger_config.print_and_log_info("destination chosen: " + str(destination))
        m3u_entry_line = self.tree_view_context_menu.selection
        
        if len(m3u_entry_line) == 0:
            logger_config.print_and_log_info("N-o line selected")
            return


        m3u_entry_id_str = m3u_entry_line['ID']
        
        directory = destination[1]
        
        self._parent.m3u_to_freebox_application.create_xspf_file_by_id_str(directory, m3u_entry_id_str)
  
    def _create_view(self):
                
        self._create_filter_frame()
        self._create_tree_view_frame()
        self._create_bottom_frame()
        


      
    def create_scrollbar(self):  
        pass

    def filter_updated(self, *args):
        if self._title_filter_text_content != self._filter_input_text.get():
            self._title_filter_text_content = self._filter_input_text.get()
            self.fill_m3u_entries()
        else:
            logger_config.print_and_log_info(f"Title filter text content not changed. Still:{self._title_filter_text_content}")


    def treeview_sort_column(self, tv, col, reverse):
        """ Sort """
        logger_config.print_and_log_info(f"Sort by column:{col}, reverse:{reverse}")
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
                self.treeview_sort_column(tv, col, not reverse))

        import main_view
        @property
        def parent(self) -> main_view.M3uToFreeboxMainView:
            return self._parent

        @parent.setter
        def parent(self, value: main_view.M3uToFreeboxMainView):
            self._parent = value


    def _reset_library(self):
        self._parent.m3u_to_freebox_application.reset_library()
        self.filter_updated()

    def _clear_list(self):
        self._tree_view.delete(* self._tree_view.get_children())


    def __get_selected_title_filter(self):
        selected_title_filter_name = self._title_filter_option_var.get()
        selected_title_filter = [filter for filter in self._by_title_filters if filter.label == selected_title_filter_name][0]
        return selected_title_filter

    def __get_selected_type_filter(self):
        selected_type_filter_name = self._type_filter_option_var.get()
        selected_type_filter = [filter for filter in self._by_type_filters if filter.label == selected_type_filter_name][0]
        return selected_type_filter
        

    def fill_m3u_entries(self):
        """ fill_m3u_entries """
        with logger_config.stopwatch_with_label("Fill m3u entries"):
            fill_m3u_entries_start_time = time.time()
            logger_config.print_and_log_info("fill_m3u_entries: begin")
            self._clear_list()
            logger_config.print_and_log_info(f"fill_m3u_entries: list reset. Elapsed:{date_time_formats.format_duration_to_string(time.time() - fill_m3u_entries_start_time)}" )
            m3u_entry_number = 0
            
            selected_title_filter = self.__get_selected_title_filter()
            selected_type_filter = self.__get_selected_type_filter()

            for m3u_entry in self._parent.m3u_to_freebox_application.m3u_library.get_m3u_entries_with_filter(self._filter_input_text.get(), selected_title_filter, selected_type_filter):
                m3u_entry_number = m3u_entry_number + 1
                tree_view_entry_values = [m3u_entry.id,m3u_entry.cleaned_title,m3u_entry.original_raw_title,m3u_entry.title_as_valid_file_name, m3u_entry.group_title, m3u_entry._type.value, m3u_entry.get_file_size_to_display()]


                self._tree_view.insert("",'end', iid=m3u_entry.id, values=tree_view_entry_values)

                if m3u_entry_number % 50000 == 0:
                    logger_config.print_and_log_info(str(m3u_entry_number) + " entries filled (in progress)")
            
            logger_config.print_and_log_info(f"fill_m3u_entries: list ended. {m3u_entry_number} entries filled. Elapsed:{date_time_formats.format_duration_to_string(time.time() - fill_m3u_entries_start_time)}")
            
    def selection(self):
        print(self.tree_view_context_menu.selection)
        

if __name__ == "__main__":
    main = importlib.import_module("main")
    main.main()
