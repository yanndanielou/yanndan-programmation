from logger import logger_config
from parsedml import parse_dml
from common import json_encoders
import param

if __name__ == "__main__":

    with logger_config.application_logger("ParseDML"):
        dml_file_content2 = parse_dml.DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path=param.DML_FILE_CLEANED_FINAL)
        row_errors = dml_file_content2.could_not_be_parsed_because_error_rows
        with open("logs/errors.txt", mode="w", encoding="utf-8") as error_file:
            error_file.write("\n".join([str(row_error) for row_error in row_errors]))
        pass
