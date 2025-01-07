# -*-coding:Utf-8 -*


#import sys

import time

import os


from logger import logger_config
from common import date_time_formats


from application import DirectoryStatsApplication
from main_view import DirectoryStatsMainView

from tkinter import Tk


def main()->None:
    """ Main function """

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("DirectoryStats")

        logger_config.print_and_log_info('Start application')

        root = Tk()
        mainview = DirectoryStatsMainView(root)
        app: DirectoryStatsApplication = DirectoryStatsApplication(mainview)
        mainview.mainloop()

        logger_config.print_and_log_info("End. Nominal end of application")

if __name__ == "__main__":
    # sys.argv[1:]
    main()
