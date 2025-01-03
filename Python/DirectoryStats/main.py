# -*-coding:Utf-8 -*

import random

#import sys

import time

import os


from Dependencies.Logger import logger_config
from Dependencies.Common import date_time_formats

from application import M3uToFreeboxApplication
from main_view import M3uToFreeboxMainView



def main():
    """ Main function """
    
    with logger_config.stopwatch_with_label("Application duration"):
        application_start_time = time.time()
        log_file_name = os.path.basename(__file__) + str(random.randrange(100000)) + ".log"
        logger_config.configure_logger(log_file_name)

        logger_config.print_and_log_info('Start application')

        mainview = M3uToFreeboxMainView()
        app: M3uToFreeboxApplication = M3uToFreeboxApplication(mainview)
        mainview.m3u_to_freebox_application = app
        mainview.mainloop()

        logger_config.print_and_log_info("End. Nominal end of application in " + date_time_formats.format_duration_to_string(
        time.time() - application_start_time))


if __name__ == "__main__":
    # sys.argv[1:]
    main()
