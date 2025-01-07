# -*-coding:Utf-8 -*

import random

#import sys

import time

import os


from Dependencies.Logger import logger_config
from Dependencies.Common import date_time_formats

import tkinter


def main()->None:
    """ Main function """
    logger_config.configure_logger_with_random_log_file_suffix("Mulitlanguage")
    
    with logger_config.stopwatch_with_label("Application duration"):
        application_start_time = time.time()
        

        logger_config.print_and_log_info('Start application')

        root = tkinter.Tk()
        root.title("Multilanguage")
        main_frame = tkinter.Frame(root)
        checkbox = tkinter.Checkbutton(main_frame, text="Checkbox 1")
        label = tkinter.Label(main_frame, text="Label 1")
        entry = tkinter.Entry(main_frame, textvariable='entry 1')
        
        phone = tkinter.StringVar()
        option_home = tkinter.Radiobutton(main_frame, text='Home', variable=phone, value='home')
        option_office = tkinter.Radiobutton(main_frame, text='Office', variable=phone, value='office')
        option_cell = tkinter.Radiobutton(main_frame, text='Mobile', variable=phone, value='cell')
        
        button = tkinter.Button(main_frame, text='button 1')

        
        checkbox.grid(row= 0, column=0)
        label.grid(row= 1, column=0)
        entry.grid(row= 2, column=0)
        option_home.grid(row= 3, column=0)
        option_office.grid(row= 3, column=1)
        option_cell.grid(row= 3, column=2)
        button.grid(row= 4, column=0)


        
        main_frame.pack()
        root.mainloop()

        logger_config.print_and_log_info("End. Nominal end of application in " + date_time_formats.format_duration_to_string(
        time.time() - application_start_time))


if __name__ == "__main__":
    # sys.argv[1:]
    main()
