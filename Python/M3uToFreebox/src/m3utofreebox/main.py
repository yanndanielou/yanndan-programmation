# -*-coding:Utf-8 -*

# import sys

import time


from logger import logger_config
from common import date_time_formats

from application import M3uToFreeboxApplication
from main_view import M3uToFreeboxMainView


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        application_start_time = time.time()
        logger_config.configure_logger_with_random_log_file_suffix("M3uToFreebox")

        logger_config.print_and_log_info("Start application")

        main_view = M3uToFreeboxMainView()
        app: M3uToFreeboxApplication = M3uToFreeboxApplication(main_view)
        main_view.m3u_to_freebox_application = app
        main_view.mainloop()

        logger_config.print_and_log_info(
            "End. Nominal end of application in "
            + date_time_formats.format_duration_to_string(time.time() - application_start_time)
        )


if __name__ == "__main__":
    # sys.argv[1:]
    main()
