import os

from logger import logger_config

from polarionextractanalysis import polarion_data_model

DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")
OUTPUT_DIRECTORY_NAME = "output"
DISPLAY_OUTPUT = False


def main() -> None:

    with logger_config.application_logger():

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        users_library = polarion_data_model.UsersLibrary(input_json_file_path=DEFAULT_DOWNLOAD_DIRECTORY + "/" + "Extraction_POLARION_User.json")
        library = polarion_data_model.PolarionLibrary(input_json_file_path=DEFAULT_DOWNLOAD_DIRECTORY + "/" + "Extraction_POLARION_Full.json", users_library=users_library)
        library.dump_to_excel_file(output_directory_path=OUTPUT_DIRECTORY_NAME)
        library.users_library.dump_to_excel_file(output_directory_path=OUTPUT_DIRECTORY_NAME)


if __name__ == "__main__":
    main()
