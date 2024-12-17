# -*-coding:Utf-8 -*

""" https://tkdocs.com/tutorial/firstexample.html """
import random


import sys

import Dependencies.Logger.logger_config as logger_config
import Dependencies.Common.date_time_formats as date_time_formats

from destinations import DestinationsFolders



import tkinter



import tkinter
#import detailspopup
#from main import main
import importlib

from m3u_search_filters import M3uEntryByTitleFilter, TitleContainsExactlyFilter, M3uFiltersManager



from tkinter import (
  filedialog, 
  simpledialog, 
  messagebox, 
  scrolledtext, 
  Menu,
  colorchooser,
  ttk
  )



class DetailsViewTab(ttk.Frame):

    
    def __init__(self, parent, tab_control):
        super().__init__(tab_control)
        
        self._paddings = {'padx': 5, 'pady': 5}

        import main_view
        self._parent:main_view.M3uToFreeboxMainView = parent
        
        self._filters:list[M3uEntryByTitleFilter] = M3uFiltersManager().filters

        self._create_view()
        self._create_context_menu()
        
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
        
        
        # output label
        self.filter_option_description_label = ttk.Label(self._filter_frame, foreground='black')
        self.filter_option_description_label['text'] = f'Type of filter:'
        self.filter_option_description_label.grid(row= 0, column=1, padx=20, pady=10)


        filters_texts = [o.label for o in self._filters]

        # set up variable
        self.option_var = tkinter.StringVar(self)
        # option menu
        self._filter_option_menu = ttk.OptionMenu(
            self._filter_frame,
            self.option_var,
            filters_texts[0],
            *filters_texts,
            command=self.filter_option_changed)
        
        
        self._filter_option_menu.grid(row= 0, column=2, padx=5, pady=10)

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

        columns = ('ID','Cleaned title','Original title', 'File name', 'Group')

        self._tree_view["column"] = columns

        for column in self._tree_view["column"]:
                self._tree_view.heading(column, text=column, command=lambda: \
                   self.treeview_sort_column(self._tree_view, column, False), anchor='center')
        

        self._tree_view.column(self._tree_view["columns"][0],width=40)
        
        #print(str(self._tree_view.column("ID")))
        #self._tree_view.column("ID")['minwidth']
        #print(str(self._tree_view.column("ID")))

        
        #['width'] = 10
        #self._tree_view.column("ID")['minwidth'] = 10
        #column_id.width = 10
    


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
        

        

        
    def filter_option_changed(self, *args):
        logger_config.print_and_log_info(f'You selected: {self.option_var.get()}')
        self.fill_m3u_entries()

        
    
    def _create_context_menu(self):
        #Create context menu
        self.tree_view_context_menu: tkinter.Menu = tkinter.Menu(self, tearoff=0)
        
        
        self.tree_view_context_menu.add_command(label="Create xspf on ...", command=self._select_directory_popup_and_create_xspf)
        
        destinations_folders  = DestinationsFolders().destinations_folders
        self.tree_view_context_menu.add_command(label="Create xspf on " + destinations_folders[0][0], command=lambda: self._create_xspf_on_destination_context_menu_choosen(destinations_folders[0]))
        self.tree_view_context_menu.add_command(label="Create xspf on " + destinations_folders[1][0], command=lambda: self._create_xspf_on_destination_context_menu_choosen(destinations_folders[1]))
        
        #for i, destination_folder in enumerate (DestinationsFolders().destinations_folders):
        #    self.tree_view_context_menu.add_command(label="Create xspf on " + destination_folder[0], command=lambda: self._create_xspf_on_destination_context_menu_choosen(destination_folder[1]))
        
        #        
        #self.tree_view_context_menu.add_command(label="Create xspf on " + destinations_folders[1][0], command=lambda: self._create_xspf_on_destination_context_menu_choosen(destinations_folders[1][1]))
        
        for destination_folder in DestinationsFolders().destinations_folders :
            print(destination_folder[0])
            print(destination_folder)
            #destination_folder_path = str(destination_folder[1)])
            #self.tree_view_context_menu.add_command(label="Create xspf on " + destination_folder[0], command=lambda: self._create_xspf_on_destination_context_menu_choosen(destination_folder[1]))
            
        self.tree_view_context_menu.add_command(label="Show detail", command=self._open_m3u_entry_detail_popup)
        self.tree_view_context_menu.add_command(label="Reset", command=self._reset_list)
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
        
    def _select_directory_popup_and_create_xspf(self):
        tree_view_selection = self._tree_view.selection()
        logger_config.print_and_log_info("tree_view_selection:"  + str(tree_view_selection))
        
        directory_path:filedialog.Directory = filedialog.askdirectory()
        directory_path_name = str(directory_path)
        logger_config.print_and_log_info("Directory chosen:" + str(directory_path_name))

        if directory_path_name != "":
            m3u_entry_line = self.tree_view_context_menu.selection
            m3u_entry_id_str = m3u_entry_line['ID']
            
            self._parent.m3u_to_freebox_application.create_xspf_file_by_id_str(directory_path_name, m3u_entry_id_str)
        else:
            logger_config.print_and_log_info("No directory chosen")

    def _create_xspf_on_destination_context_menu_choosen(self, destination):
        logger_config.print_and_log_info("destination chosen: " + str(destination))
        m3u_entry_line = self.tree_view_context_menu.selection
        
        if len(m3u_entry_line) == 0:
            logger_config.print_and_log_info("No line selected")
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
        filter_text = self._filter_input_text.get()
        self.fill_m3u_entries()


    def treeview_sort_column(self, tv, col, reverse):
        """ Sort """
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

    def _reset_list(self):
        self._tree_view.delete(* self._tree_view.get_children())



    def fill_m3u_entries(self):
        """ fill_m3u_entries """
        self._reset_list()
        m3u_entry_number = 0
        
        selected_filter_name = self.option_var.get()
        
        selected_filter = [filter for filter in self._filters if filter.label == selected_filter_name][0]
        
        for m3u_entry in self._parent.m3u_to_freebox_application.m3u_library.get_m3u_entries_with_filter(self._filter_input_text.get(), selected_filter):
            m3u_entry_number = m3u_entry_number + 1
            self._tree_view.insert("",'end', iid=m3u_entry.id, values=(m3u_entry.id,m3u_entry.cleaned_title,m3u_entry.original_raw_title,m3u_entry.title_as_valid_file_name, m3u_entry.group_title))

            if m3u_entry_number % 10000 == 0:
                logger_config.print_and_log_info(str(m3u_entry_number) + " entries filled (in progress)")
        
        logger_config.print_and_log_info(str(m3u_entry_number) + " entries filled (end)")
        
    def selection(self):
        print(self.tree_view_context_menu.selection)
        

if __name__ == "__main__":
    main = importlib.import_module("main")
    main.main()
