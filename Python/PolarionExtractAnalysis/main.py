import os

from logger import logger_config

OUTPUT_DIRECTORY_NAME = "output"
DISPLAY_OUTPUT = False


def main() -> None:
    """Main function"""

    with logger_config.application_logger():

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)


if __name__ == "__main__":
    # sys.argv[1:]
    main()
