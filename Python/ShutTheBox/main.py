# -*-coding:Utf-8 -*
""" Main """
from logger import logger_config
from shutthebox.application import Application


def main()->None:
    """ Main function """

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("CloseTheBox")

        logger_config.print_and_log_info('Start application')
        application:Application = Application()
        application.run()




        logger_config.print_and_log_info("End. Nominal end of application")

if __name__ == "__main__":
    # sys.argv[1:]
    main()
