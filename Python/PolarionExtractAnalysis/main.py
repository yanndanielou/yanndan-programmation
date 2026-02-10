import os

from logger import logger_config

from polarionextractanalysis import polarion_data_model

OUTPUT_DIRECTORY_NAME = "output"
DISPLAY_OUTPUT = False


def main() -> None:

    with logger_config.application_logger():
        input_file = r"C:\Users\fr232487\Downloads\Extraction_POLARION_Full.json"

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        library = polarion_data_model.PolarionLibrary(input_json_file_path=input_file)
        library.dump_to_excel_file(output_directory_path=OUTPUT_DIRECTORY_NAME)
        library.users_library.dump_to_excel_file(output_directory_path=OUTPUT_DIRECTORY_NAME)


if __name__ == "__main__":
    main()
