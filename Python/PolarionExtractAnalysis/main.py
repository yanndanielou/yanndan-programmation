import os

from logger import logger_config

from polarionextractanalysis import polarion_data_model

OUTPUT_DIRECTORY_NAME = "output"
DISPLAY_OUTPUT = False


def main() -> None:
    """Main function"""

    with logger_config.application_logger():
        input_file = r"C:\Users\fr232487\Downloads\Extraction_POLARION_Full.json"
        polarion_data_model.PolarionLibrary(input_json_file_path=input_file)

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)


if __name__ == "__main__":
    # sys.argv[1:]
    main()
